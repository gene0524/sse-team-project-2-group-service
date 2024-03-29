from flask import Flask, jsonify, request
from flask_cors import CORS
from database_functions import (
    create_group,
    display_user_groups,
    accept_group_invitation,
    decline_group_invitation,
    remove_group,
    display_group_members,
    display_top_votes,
    display_vote_options,
    click_vote_dish,
    cancel_vote,
    add_food_to_groups,
)

app = Flask(__name__)
CORS(app)

##### user_groups.html #####


# Function to create a group
@app.route("/create-group", methods=["POST"])
def app_create_group():
    try:
        group_data = request.json
        create_group(
            group_name=group_data.get("groupName"),
            email_list=group_data.get("groupMembers"),
            description=group_data.get("groupDetail"),
        )
        return jsonify(message="Group data received successfully")
    except Exception as e:
        return jsonify(error=str(e)), 500


# Function to display the groups that this user is part of / is invited
@app.route("/display-user-groups", methods=["POST"])
def app_display_user_groups():
    try:
        request_data = request.json
        user_email = request_data.get("userEmail")
        groups = display_user_groups(user_email)
        # groups = [
        #     {'group_name': group_name, 'description': description, 'group_id': group_id, 'status': status},
        #     {'group_name': group_name, 'description': description, 'group_id': group_id, 'status': status},
        #     {'group_name': group_name, 'description': description, 'group_id': group_id, 'status': status}
        # ]
        print(groups)
        return jsonify(groups)
    except Exception as e:
        return jsonify(error=str(e)), 500


# Route to accept a group invitation
@app.route("/accept-group", methods=["POST"])
def app_accept_group():
    try:
        request_data = request.json
        group_id = request_data.get("group_id")
        email = request_data.get("email")
        result = accept_group_invitation(group_id, email)
        if result:
            return jsonify(message="Group invitation accepted successfully")
        else:
            return jsonify(error="Failed to accept the group invitation"), 500
    except Exception as e:
        return jsonify(error=str(e)), 500


# Route to decline a group invitation
@app.route("/decline-group", methods=["POST"])
def app_decline_group():
    try:
        request_data = request.json
        group_id = request_data.get("group_id")
        email = request_data.get("email")
        result = decline_group_invitation(group_id, email)
        if result:
            return jsonify(message="Group invitation declined successfully")
        else:
            return jsonify(error="Failed to decline the group invitation"), 500
    except Exception as e:
        return jsonify(error=str(e)), 500


# Function to remove a group for the member
@app.route("/remove-group", methods=["POST"])
def app_remove_group():
    try:
        request_data = request.json
        group_id = request_data.get("group_id")
        email = request_data.get("email")
        result = remove_group(group_id, email)

        if result:
            return jsonify(message="Group removed successfully")
        else:
            return jsonify(error="Failed to remove group"), 500
    except Exception as e:
        return (jsonify(error=str(e)),)


##### group_info.html #####


# Function to display the group members in a specified group
@app.route("/display-group-members", methods=["POST"])
def app_display_group_members():
    try:
        request_data = request.json
        group_id = request_data.get("groupId")
        members = display_group_members(group_id)
        # members = [
        #     {'email': email, 'first_name': first_name,'last_name': last_name,'stauts': stauts},
        #     {'email': email, 'first_name': first_name,'last_name': last_name,'stauts': stauts},
        #     {'email': email, 'first_name': first_name,'last_name': last_name,'stauts': stauts}
        # ]
        print(members)
        return jsonify(members)
    except Exception as e:
        return jsonify(error=str(e)), 500


# Function to display the top dish url that has the most votes (LIMIT 5)
@app.route("/display-top-votes", methods=["POST"])
def app_display_top_votes():
    try:
        request_data = request.json
        group_id = request_data.get("groupId")
        top_votes = display_top_votes(group_id)
        # top_votes = [
        #     {'dish_uri': dish_uri},
        #     {'dish_uri': dish_uri},
        #     {'dish_uri': dish_uri}
        # ]
        return jsonify(top_votes)
    except Exception as e:
        return jsonify(error=str(e)), 500


##### voting.html #####


# Function to display the food options to vote (include a flag whether this user has voted for each food)
@app.route("/display-vote-options", methods=["POST"])
def app_display_vote_options():
    try:
        request_data = request.json
        group_id = request_data.get("groupId")
        user_email = request_data.get("userEmail")
        dish_options = display_vote_options(group_id, user_email)
        # dishes = [
        #     {'dish_uri': dish_uri, 'votes_count': 3, 'voted_by_user': 0},
        #     {'dish_uri': dish_uri, 'votes_count': 2, 'voted_by_user': 1},
        #     {'dish_uri': dish_uri, 'votes_count': 5, 'voted_by_user': 1}
        # ]
        return jsonify(dish_options)
    except Exception as e:
        return jsonify(error=str(e)), 500


# Function to vote for a dish (check if total votes have exceeded 3)
@app.route("/click-vote-dish", methods=["POST"])
def app_click_vote_dish():
    try:
        request_data = request.json
        group_id = request_data.get("groupId")
        user_email = request_data.get("userEmail")
        dish_uri = request_data.get("dishUri")
        click_vote_dish(group_id, user_email, dish_uri)
        return jsonify(message="Vote registered successfully")
    except Exception as e:
        return jsonify(error=str(e)), 500


# Function to cancel the vote for a dish
@app.route("/cancel-vote-dish", methods=["POST"])
def app_cancel_vote_dish():
    try:
        request_data = request.json
        group_id = request_data.get("groupId")
        user_email = request_data.get("userEmail")
        dish_uri = request_data.get("dishUri")
        cancel_vote(group_id, user_email, dish_uri)
        return jsonify(message="Vote registered successfully")
    except Exception as e:
        return jsonify(error=str(e)), 500


##### profile.html #####


# Function to add a food to Group Food List table
@app.route("/add-food-to-groups", methods=["POST"])
def app_add_food_to_groups():
    try:
        request_data = request.json
        email = request_data.get("userEmail")
        dish_uri = request_data.get("dishUri")
        result = add_food_to_groups(email, dish_uri)
        print(result)
        if result:
            return jsonify(message="Food added successfully")
        else:
            return jsonify(message="Not a member in any groups!")
    except Exception as e:
        return jsonify(error=str(e)), 500
