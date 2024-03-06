from dotenv import load_dotenv
import supabase
import os

load_dotenv()

# Constants for Supabase URL and API keys
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize the Supabase Client
supabase_client = supabase.create_client(SUPABASE_URL, SUPABASE_KEY)

##### user_groups.html #####

# Function to create a group
def create_group(group_name, email_list, description):
    group_data = add_group_to_groupbase(group_name, description)
    group_id = group_data[0]['group_id'] # retrieve group_id

    # Set first person in the email list as the group owner (status 2)
    add_member_to_group(group_id, email_list[0], 2)
    # Set other members' status to pending (status 0) by default
    for email in email_list[1:]:
        add_member_to_group(group_id, email, 0)
    return

# subfunction of create_group(), add the group to Group Registration table
def add_group_to_groupbase(group_name, description):
    data_to_insert = {
        "group_name": group_name,
        "description": description
    }
    data, _ = supabase_client.table("Group Registration").insert([data_to_insert]).execute()
    return data[1]

# subfunction of create_group(), add the member to Group Members Info table
def add_member_to_group(group_id, email, status):
    data_to_insert = {
        "group_id": group_id,
        "email": email,
        "status": status
    }
    supabase_client.table("Group Members Info").insert([data_to_insert]).execute()
    return

# Function to display the groups that this user is part of / is invited
def display_user_groups(user_email):
    response, _ = supabase_client.table("Group Members Info")\
                    .select("group_id, status, Group Registration (group_name, description)")\
                    .eq("email", user_email)\
                    .execute()
    
    response_list = response[1]
    
    groups = [
        {
            'group_name': group['Group Registration']['group_name'],
            'description': group['Group Registration']['description'],
            'group_id': group['group_id'],
            'status': group['status']
        } for group in response_list
    ]
    return groups

##### group_info.html #####

# Function to display the group members in a specified group
def display_group_members(group_id):
    response, _ = supabase_client.table("Group Members Info")\
                        .select("email, status, User Registration (firstname, lastname)")\
                        .eq("group_id", group_id)\
                        .execute()
    response_list = response[1]
    members = [
        {
            'email': member['email'],
            'first_name': member['User Registration']['firstname'],
            'last_name': member['User Registration']['lastname'],
            'status': member['status']
        } for member in response_list
    ]
    print(members)
    return members

display_group_members(1)

# Function to delete a member from the group
def delete_member_from_group(group_id, email):
    # Check the status of the member in the group
    response, _ = supabase_client.table("Group Members Info")\
                    .select("status")\
                    .eq("group_id", group_id)\
                    .eq("email", email)\
                    .execute()

    # If there is an error or no data found, return an error message
    if not response:
        print("Error: Failed to retrieve member status or member does not exist.")
        return {'error': 'Failed to retrieve member status or member does not exist.'}

    # If the status of the member is 2, they are the owner and cannot be deleted
    member_status = response[1][0]["status"]
    if member_status == 2:
        print("Error: Cannot delete group owner.")
        return {'error': 'Cannot delete group owner.'}

    # If the member is not the owner, proceed to delete them from the group
    data, _ = supabase_client.table("Group Members Info").delete()\
                    .eq("group_id", group_id)\
                    .eq("email", email)\
                    .execute()
    if data[1]:
        print("Successfully deleted!")
    return data[1]

# Function to delete the group
# TODO: Check that only the owner can delete the group
def delete_group(group_id):
    data, _ = supabase_client.table("Group Registration").delete().eq("group_id", group_id).execute()
    return data[1]

# Function to display the top dish url that has the most votes (LIMIT 5)
def display_top_votes(group_id):
    voted_food, _ = supabase_client.table("Group Food List")\
                    .select("dish_uri")\
                    .eq("group_id", group_id)\
                    .gt("votes_count", 0)\
                    .order("votes_count", desc=True)\
                    .limit(5)\
                    .execute()
    voted_food_list = voted_food[1]
    return voted_food_list

##### vote.html #####

# Function to display the food options to vote (include a flag whether this user has voted for each food)
def display_vote_options(group_id, user_email):
    response_1, _ = supabase_client.table("Group Food List")\
                    .select("dish_uri, votes_count")\
                    .eq("group_id", group_id)\
                    .execute()
    
    dish_list = response_1[1]
    
    response_2, _ = supabase_client.table("Group Vote")\
                    .select("dish_uri")\
                    .eq("group_id", group_id).eq("email", user_email)\
                    .execute()

    options_voted = response_2[1]
    
    # Create a list of dish_uris that the user has voted for
    voted_list = [vote['dish_uri'] for vote in options_voted]  
    
    dishes = [
        {
            'dish_uri': dish['dish_uri'],
            'votes_count': dish['votes_count'],
            'voted_by_user': dish['dish_uri'] in voted_list
        } for dish in dish_list
    ]
    return dishes

# Function to vote for a dish (check if total votes have exceeded 3)
# TODO: whether the number of votes should be unified to 3
def click_vote_dish(group_id, user_email, dish_uri):
    valid_click = False
    
    # Give the count of how many times this user has voted
    num_voted, _ = supabase_client.table("Group Vote")\
                    .select('*')\
                    .eq("group_id", group_id)\
                    .eq("email", user_email)\
                    .execute()
    count = len(num_voted[1])
    
    # Validate if the user has the right to vote (owner)
    if count < 3:
        valid_click = True
    
    # If valid to vote, add the dish uri to the table
    if valid_click:
        data_to_insert = {
            'group_id': group_id,
            'dish_uri': dish_uri,
            'email': user_email
        }
        # Insert the data into Group Vote
        data, _ = supabase_client.table("Group Vote")\
                    .insert([data_to_insert])\
                    .execute()
        
        # Get the updated count
        new_count, _ = supabase_client.table("Group Vote")\
                    .select('*')\
                    .eq("group_id", group_id)\
                    .eq("dish_uri", dish_uri)\
                    .execute()
        new_count = len(new_count[1])
        
        # Update the vote count in the Group Food List table
        data, _ = supabase_client.table("Group Food List")\
                    .update({"votes_count": new_count})\
                    .eq("dish_uri", dish_uri)\
                    .eq("group_id", group_id)\
                    .execute()
        print("Successfully voted")
    else:
        print("Vote is not successful. Check your condition")
        

##### user_favorites.html & search_result.html #####

# Function to add a food to Group Food List table
def add_food_to_group(group_id, dish_uri):
    data_to_insert = {
        "group_id": group_id,
        "dish_uri": dish_uri,
        "votes_count": 0
    }
    data, _ = supabase_client.table("Group Food List").insert([data_to_insert]).execute()
    return data[1]