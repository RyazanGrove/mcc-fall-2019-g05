import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage
from firebase_admin import db
from firebase_admin import auth
from firebase_admin import messaging
from google.cloud import storage

import flask
from flask import request
from flask import send_file
from flask import jsonify

import traceback
import os
import json
import time
from datetime import datetime

import atexit
from apscheduler.schedulers.background import BackgroundScheduler



# Check if db activating first time
if not len(firebase_admin._apps):

    # Fetch the service account key JSON file contents
    cred = credentials.Certificate('cred.json')

    # Initialize the app with a service account, granting admin privileges
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://mcc-fall-2019-g5-258415.firebaseio.com/'
    })

    # Credentials for google cloud storage
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "cred.json"

ref = db.reference('/')


import firebase_interaction as bfi
import FB_functions
import report_generate
import image_functions as img_func


app = flask.Flask(__name__)
app.config["IMAGE_UPLOADS"] = "img/uploads"


def get_uid_from(id_token):
    '''
    Function verifying token from client.
    Returns uid which can be used for user identifying.
    '''

    try:
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']

        return uid

    except:

        return 'ERROR: Authenfication failed.'


def user_validate(uid_response, project_id):

    if(uid_response == "ERROR: Authenfication failed."):
        return "ERROR: Authenfication failed."

    #check that user exists
    if(not(FB_functions.verify_user(uid_response))):
        return "ERROR: Not such user."

    if(not(FB_functions.does_user_in_project(uid_response, project_id))):
        return "ERROR: User not in project"

    return 'OK'


@app.route('/')
def default_route():
    return 'Hello world!'


@app.route('/first_set_data', methods=['GET'])
def first_set_data():
    bfi.table_fill()
    return 'INFO::Table filling is done.'


@app.route('/update_data')
def update_data():
    pass


@app.route('/project/<project_id>/upload_image', methods=['POST'])
def upload_image_to_project(project_id):

    image = request.files["image"]
    data = request.headers

    try:

        # user_id = get_uid_from(data['Firebase-Token']) # add user checking
        user_id = 'uid2'
        filename = image.filename

        # Save image locally
        # image.save(os.path.join(app.config["IMAGE_UPLOADS"], filename))
        image.save('img/' + filename)
        images_names = img_func.image_resize('img/', filename)

        save_to_fb_dir = 'attachments/' + project_id + '/'

        img_func.image_upload('img/', save_to_fb_dir, images_names)

        for element in images_names:
            FB_functions.add_attachment(
                    project_id,
                    filename,
                    save_to_fb_dir + element,
                    'image')
            os.remove('img/{}'.format(element))

        return 'INFO: Image uploaded.'

    except Exception as e:
        return 'ERROR: Image was not uploaded.\nException: {}\n{}'.format(e, traceback.print_exc())


# TODO: Fix this function to post according to new requirements
@app.route('/project/<project_id>/set_icon', methods=['POST'])
def upload_project_icon(project_id):

    image = request.files["image"]
    data = request.headers

    try:
        user_id = get_uid_from(data['Firebase-Token'])
        filename = image.filename

        # Save image locally
        # image.save(os.path.join(app.config["IMAGE_UPLOADS"], filename))
        image.save('img/' + filename)
        images_names = img_func.image_resize('img/', filename)

        save_to_fb_dir = 'attachments/' + project_id + '/icon/'

        img_func.image_upload('img/', save_to_fb_dir, images_names)

        FB_functions.update_project(project_id, 'image_url', save_to_fb_dir)

        for element in images_names:
            FB_functions.add_attachment(
                    project_id,
                    filename,
                    save_to_fb_dir + element,
                    'project_icon')
            os.remove('img/{}'.format(element))

        return 'INFO: Image uploaded.'

    except Exception as e:
        return 'ERROR: Project icon was not uploaded.\nException: {}\n{}'.format(e, traceback.print_exc())


@app.route('/user/set_icon', methods=['POST'])
def upload_user_icon():

    image = request.files["image"]
    data = request.headers

    try:
        # user_id = get_uid_from(data['id_token']) # add user checking
        user_id = get_uid_from(data['Firebase-Token'])
        filename = image.filename

        # Save image locally
        # image.save(os.path.join(app.config["IMAGE_UPLOADS"], filename))
        image.save('img/' + filename)
        images_names = img_func.image_resize('img/', filename)

        save_to_fb_dir = 'attachments/' + user_id + '/'

        img_func.image_upload('img/', save_to_fb_dir, images_names)

        for element in images_names:
            os.remove('img/{}'.format(element))

        return 'INFO: User icon uploaded.'

    except Exception as e:
        return 'ERROR: Project icon was not uploaded.\nException: {}\n{}'.format(e, traceback.print_exc())


# TODO: Fix this function
@app.route('/get_image/<path>/<filename>', methods=['GET'])
def get_image(path, filename):

    data = request.get_json()
    quality = data['quality']

    img_func.image_download(path + '/', filename, quality)

    return 'INFO::Image downloaded'


@app.route('/user', methods=['GET'])
def get_user():

    #check for valid token
    id_token = request.headers["Firebase-Token"]
    uid_response = get_uid_from(id_token)

    if(uid_response == "ERROR: Authenfication failed."):
        return "ERROR: Authenfication failed."

    #check that user exists
    if(not(FB_functions.verify_user(uid_response))):
        return "ERROR: Not such user."

    return json.dumps(FB_functions.return_certain_user(uid_response))


@app.route('/users', methods=['GET'])
def get_all_users():

    #check for valid token
    id_token = request.headers["Firebase-Token"]
    uid_response = get_uid_from(id_token)

    if(uid_response == "ERROR: Authenfication failed."):
        return "ERROR: Authenfication failed."

    #check that user exists
    if(not(FB_functions.verify_user(uid_response))):
        return "ERROR: Not such user."

    return json.dumps(FB_functions.return_all_users())


@app.route('/user/update', methods=['PUT'])
def update_user():

    #check for valid token
    id_token = request.headers["Firebase-Token"]
    uid_response = get_uid_from(id_token)

    if(uid_response == "ERROR: Authenfication failed."):
        return "ERROR: Authenfication failed."

    #check that user exists
    if(not(FB_functions.verify_user(uid_response))):
        return "ERROR: Not such user."

    data = request.get_json()

    return str(FB_functions.update_user(uid_response,data))


@app.route('/user/create', methods=['POST'])
def create_user():

    data = request.get_json()
    id_token = request.headers["Firebase-Token"]
    uid_response = get_uid_from(id_token)

    if(uid_response == "ERROR: Authenfication failed."):
        return "ERROR: Authenfication failed."

    FB_functions.create_user(uid_response, data["name"], data["email"])

    return 'OK'


@app.route('/user/unique/<username>', methods=['GET'])
def is_user_unique(username):

    reply = []

    if FB_functions.user_is_unique(username):
        return jsonify(reply)

    else:
        username_options = FB_functions.unique_names(username)
        return jsonify(username_options)


@app.route('/project/create', methods=['POST'])
def create_project():

    data = request.get_json()
    id_token = request.headers["Firebase-Token"]
    uid_response = get_uid_from(id_token)

    if(uid_response == "ERROR: Authenfication failed."):
        return "ERROR: Authenfication failed."

    if(not(FB_functions.verify_user(uid_response))):
        return "ERROR: Not such user."

    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

    project_id = FB_functions.create_project(
            data['title'],
            data['is_shared'],
            data['key_words'],
            uid_response,
            data['deadline'],
            data['description'],
            '',
            dt_string,
            False
    )

    return project_id


@app.route('/project/<project_id>/delete', methods=['DELETE'])
def delete_project(project_id):

    #check for valid token
    id_token = request.headers["Firebase-Token"]
    uid_response = get_uid_from(id_token)

    if(uid_response == "ERROR: Authenfication failed."):
        return "ERROR: Authenfication failed."

    #check that user exists
    if(not(FB_functions.verify_user(uid_response))):
        return "ERROR: Not such user."

#    if user_validate(uid_response, project_id) == 'OK' and \
    if(FB_functions.does_user_admin_of_project(uid_response, project_id)):
        return FB_functions.delete_project(project_id)

    else:
        return "ERROR: user does not have rights to delete project"


# TODO: Set members functionality
@app.route('/project/<project_id>/members/set', methods=['POST'])
def add_members_to_project(project_id):

    #check for valid token
    id_token = request.headers["Firebase-Token"]
    uid_response = get_uid_from(id_token)

    if user_validate(uid_response, project_id) == 'OK':
        return FB_functions.add_members_to_project(users_id, project_id)
    else:
        return 'ERROR: Your user not have permissions to do this.'


@app.route('/project/<project_id>/members', methods=['GET'])
def get_members_of_project(project_id):
    '''
    Returns dict of members which consist of user_id, project_id and role_id
    '''

    #check for valid token
    id_token = request.headers["Firebase-Token"]
    uid_response = get_uid_from(id_token)

    if user_validate(uid_response, project_id) == 'OK':
        members = FB_functions.get_members_of_project(project_id)
        return json.dumps(members)
    else:
        return 'ERROR: Your user not have permissions to do this.'


@app.route('/project/<project_id>/tasks/add', methods=['POST'])
def set_task_to_project(project_id):

    #check for valid token
    id_token = request.headers["Firebase-Token"]
    uid_response = get_uid_from(id_token)

    if user_validate(uid_response, project_id) == 'OK':

        if "assignee_id" not in data:
            data["assignee_id"] = uid_response

        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        data["createdAt"] = dt_string
        data["status"] = 'pending'

        data=request.args

        task_id = FB_functions.add_task(
                project_id,
                uid_response,
                data["assignee_id"],
                data["description"],
                data["deadline"],
                data["createdAt"],
                data["status"]
        )

        return json.dumps(task_id)

    else:
        return 'ERROR: Your user not have permissions to do this.'


# Add to this function checking if field exists
# Remove old values. Add new.
@app.route('/project/<project_id>/update', methods=['PUT'])
def project_update(project_id):

    data=request.json

    id_token = request.headers["Firebase-Token"]
    uid_response = get_uid_from(id_token)

    param_name = data['parameter']
    param_value = data['value']

    res = FB_functions.update_project(project_id, param_name, param_value)

    return jsonify(res)


# Add task assign functionality
@app.route('/task/<task_id>/update', methods=['PUT'])
def update_task_status(task_id):

    data=request.json

    id_token = request.headers["Firebase-Token"]
    uid_response = get_uid_from(id_token)

    FB_functions.update_task(task_id, data["task_status"])

    return "OK"


@app.route('/task/<task_id>/assign_to_user', methods=['POST'])
def assign_task_to_users(task_id):

    data=request.json

    id_token = request.headers["Firebase-Token"]
    uid_response = get_uid_from(id_token)

    FB_functions.assign_task_to_users(task_id, data["user_ids"])

    return "OK"


@app.route('/project/<project_id>/tasks', methods=['GET'])
def get_tasks_of_project(project_id):
    '''
    Get_tasks_of_project method.
    Returns list of tasks.
    '''

    id_token = request.headers["Firebase-Token"]
    uid_response = get_uid_from(id_token)

    tasks = FB_functions.get_tasks_of_project(project_id)

    return json.dumps(tasks)


@app.route('/project/<project_id>/attachments', methods=['GET'])
def get_attachments_of_project(project_id):

    id_token = request.headers["Firebase-Token"]
    uid_response = get_uid_from(id_token)

    list_of_attachments = FB_functions.get_attachments_of_project(project_id)

    return json.dumps(list_of_attachments)


@app.route('/project/<project_id>/attachments/add', methods=['POST'])
def add_attachments_to_project(project_id):
    return "This is add_attachments_to_project method. returns fails or not"


@app.route('/project/<project_id>/generate_report')
def generate_project_report(project_id):
    '''
    This is generate_project_report method.
    Returns report file.
    '''

    id_token = request.headers["Firebase-Token"]
    uid_response = get_uid_from(id_token)

    report_name = report_generate.generate_project_report(project_id)

    send_file(report_name)

    os.remove('img/{}'.format(report_name + '.html'))
    os.remove('img/{}'.format(report_name + '.pdf'))

    return 'OK'


@app.route('/projects', methods=['GET'])
def get_list_of_projects():
    '''
    Get_list_of_projects method.
    Returns list of projects with all provided information.
    '''

    id_token = request.headers["Firebase-Token"]
    uid_response = get_uid_from(id_token)

    list_of_projects = FB_functions.get_list_of_projects_implementation(uid_response)
    return json.dumps(list_of_projects)


@app.route('/project/<project_id>', methods=['GET'])
def search_for_project(project_id):
    '''
    Search_for_project method. Searching for single project.
    Returns json with all information about project.
    '''
    id_token = request.headers["Firebase-Token"]
    uid_response = get_uid_from(id_token)

    project = FB_functions.search_for_project_implementation(project_id)

    return json.dumps(project)


@app.route('/notification_scheduler/start')
def start_notification_scheduler():

    data = request.json

    scheduler = BackgroundScheduler()
    scheduler.add_job(func=check_deadlines, trigger="interval", seconds=30)
    scheduler.start()

    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())

    return "This is send_notification method. sends a notification"

@app.route('/project/<project_id>/favorite_project', methods=['POST'])
def add_favorite_project1(project_id):
    id_token = request.headers["Firebase-Token"]
    uid_response = get_uid_from(id_token)

    return str(FB_functions.make_favorite(uid_response,project_id))


@app.route('/project/<project_id>/delete_favorite_project', methods=['DELETE'])
def delete_favorite_project1(project_id):
    id_token = request.headers["Firebase-Token"]
    uid_response = get_uid_from(id_token)

    return str(FB_functions.make_unfavorite(uid_response,project_id))


def days_between(d1, d2):

    d1 = datetime.strptime(d1, "%d/%m/%Y")
    d2 = datetime.strptime(d2, "%d/%m/%Y")

    return abs((d2 - d1).days)


def check_deadlines():

    projects_ref = ref.child('projects')
    projects = projects_ref.get()

    tasks_ref = ref.child('tasks')
    tasks = tasks_ref.get()

    users_ref = ref.child('users')
    users = users_ref.get()

    now = datetime.now()
    today = now.strftime("%d/%m/%Y")

    for project_id in projects:

        project = projects[project_id]
        deadline = project['deadline']
        deadline = deadline.split()[0]

        if days_between(today, deadline) < 2:
            connected_users = FB_functions.get_members_of_project(project_id)
            send_notification(connected_users, project['title'])
            # print('{} expires in {} days'.format(project_id, days_between(today, deadline)))


    for task_id in tasks:

        task = tasks[task_id]
        deadline = task['deadline']
        deadline = deadline.split()[0]

        if days_between(today, deadline) < 2:
            connected_users = FB_functions.get_users_by_id(FB_functions.get_users_on_task(project_id))
            send_notification(connected_users, task['id'])
            # print('{} expires in {} days'.format(task_id, days_between(today, deadline)))


def send_notification(connected_users, element_name):

    # registration_token = 'eMk-_0csB7k:APA91bGGKsCU60_tuDGAG_vgL5bNWYgbV2Utoh2ERgQFRRDAUMq_oaoFMLWq5R5w5qTZfVIm1WOTDmpRbXQA0KN38jDL6K5ShLYtFECjTLxARAc_jpfTA3w3id3y7kTV8ww3pmDbPY8k'

    # See documentation on defining a message payload.
    try:
        for user in connected_users:

            registration_token = user['registration_token']

            message = messaging.Message(
                data = '{} expires in 1 day.'.format(element_name),
                token = registration_token,
            )

            # Send a message to the device corresponding to the provided
            # registration token.
            response = messaging.send(message)

        return True

    except:
        return False


if __name__ == "__main__":

    app.run(host='0.0.0.0', debug = True, port = 8080)
