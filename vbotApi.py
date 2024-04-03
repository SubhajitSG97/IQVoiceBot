import copy
import datetime
import json
import uuid

import requests

import jiraDTO
import freshDeskDTO

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://voicebot:voicebot@localhost:5432/voicebot'
db = SQLAlchemy(app)


class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    number = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    serviceId = db.Column(db.String(255), nullable=False)
    serviceType = db.Column(db.String(50), nullable=False)
    pincode = db.Column(db.String(255), nullable=False)
    plan = db.Column(db.String(255))
    callSessionId = db.Column(db.String(255))
    dues = db.Column(db.Integer)


class JiraDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jiraId = db.Column(db.String(255))
    customerId = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    creationTime = db.Column(db.DateTime, default=datetime.datetime.now())
    description = db.Column(db.Text, nullable=True)
    issueType = db.Column(db.String(120))
    callSessionId = db.Column(db.String(255))
    transcription = db.Column(db.Text)
    recordingURL = db.Column(db.Text)

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customerId = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    amount = db.Column(db.Integer, nullable=True)
    date = db.Column(db.DateTime, default=datetime.datetime.now())



@app.route('/customer/create', methods=['POST'])
def create_user():
    data = request.get_json()
    name = data['name']
    email = data['email']
    number = data['number']
    city = data['city']
    address = data['address']
    serviceId = data['serviceId']
    serviceType = data['serviceType']
    plan = data['plan']
    pincode = data['pincode']
    dues = data['dues']
    new_customer = Customer(name=name, email=email, number=number, city=city, address=address, serviceId=serviceId,
                            serviceType=serviceType, plan=plan, pincode=pincode, dues=dues)
    db.session.add(new_customer)
    db.session.commit()
    return jsonify({'message': 'Customer created successfully'}, ), 201


@app.route('/customer/get/<int:id>', methods=['GET'])
def get_user(id):
    customer = Customer.query.get(id)
    if customer:
        return jsonify({'id': customer.id, 'name': customer.name, 'email': customer.email})
    else:
        return jsonify({'message': 'User not found'}), 404

@app.route('/customer/update', methods=['PUT'])
def update_user():
    number = request.args.get('number')
    callSessionId = request.args.get('callSessionId')
    customer = Customer.query.filter_by(number=number).first()
    # jiraTest = copy.deepcopy(jiraDTO.jiraSample)
    # createJira(jiraTest, "Kolkata","Broadband","9811590799")
    # freshdeskTicket = copy.deepcopy(freshDeskDTO.freshdeskSample)
    # createFreshdesk(freshdeskTicket,"Kolkata","Broadband","9811590799")
    if customer:
        customer.callSessionId = callSessionId
        db.session.commit()
        return jsonify({'message': 'customer updated successfully'})
    else:
        return jsonify({'message': 'customer not found'}), 404

@app.route('/customer/update/all', methods=['PUT'])
def update_details_customer():
    data = request.get_json()
    name = data['name']
    email = data['email']
    number = data['number']
    city = data['city']
    address = data['address']
    serviceId = data['serviceId']
    serviceType = data['serviceType']
    plan = data['plan']
    pincode = data['pincode']
    dues = data['dues']

    customer = Customer.query.filter_by(number=number).first()
    if customer:
        customer.name = name
        customer.email = email
        customer.city = city
        customer.address = address
        customer.serviceId = serviceId
        customer.serviceType = serviceType
        customer.plan = plan
        customer.pincode = pincode
        customer.dues = dues
        db.session.commit()
        return jsonify({'message': 'customer updated successfully'})
    else:
        return jsonify({'message': 'customer not found'}), 404

@app.route('/freshdesk/create', methods=['POST'])
def create_freshdeks():
    callSessionId = request.args.get('callSessionId')
    data = request.get_json()
    address = data['address']
    pincode = data['pincode']
    customer = Customer.query.filter_by(callSessionId=callSessionId).first()
    description = address + " " + pincode
    new_ticket = JiraDetails(customerId=customer.id, description=description, issueType="Request")
    db.session.add(new_ticket)
    db.session.commit()
    freshdeskTicket = copy.deepcopy(freshDeskDTO.freshdeskSample)
    ticketId = createFreshdesk(freshdeskTicket, address, pincode, customer)
    new_ticket.jiraId = ticketId
    db.session.commit()
    # sms && update jiraTicket on JiraDetails
    if customer:
        customer.callSessionId = callSessionId
        db.session.commit()
        return jsonify({'message': 'ticket created successfully'})



@app.route('/customer/get', methods=['GET'])
def get_customer_by_callSessionId():
    callSessionId = request.args.get('callSessionId')
    customer = Customer.query.filter_by(callSessionId=callSessionId).first()
    if customer:
        return jsonify({"id":customer.id,"name":customer.name, "email":customer.number, "plan":customer.plan, "serviceType":customer.serviceType, "serviceId":customer.serviceId, "callSessionId":customer.callSessionId, "city":customer.city, "address":customer.address, "pincode":customer.pincode, "dues":customer.dues})
    else:
        return jsonify({'message': 'customer not found'}), 404

@app.route('/customer/payment-details', methods=['GET'])
def get_payment_details():
    callSessionId = request.args.get('callSessionId')
    customer = Customer.query.filter_by(callSessionId=callSessionId).first()
    if customer:
        payments = Payment.query.filter_by(customerId=customer.id)
        return jsonify({"customerDetails":{"id":customer.id,"name":customer.name, "email":customer.number, "plan":customer.plan, "serviceType":customer.serviceType, "serviceId":customer.serviceId, "callSessionId":customer.callSessionId, "city":customer.city, "address":customer.address, "pincode":customer.pincode, "dues":customer.dues},
                        "payments":payments})
    else:
        return jsonify({'message': 'customer not found'}), 404

@app.route('/payments/create', methods=['POST'])
def create_payment():
    data = request.get_json()
    customerId = data['customerId']
    amount = data['amount']
    date = datetime.datetime.now()


    newPayment = Payment(customerId=customerId, amount=amount, date=date)
    db.session.add(newPayment)
    db.session.commit()
    return jsonify({'message': 'payment successful'}, ), 201

def createJira(new_jira_ticket, address, issueType, number):
    jiraTicket = copy.deepcopy(jiraDTO.jiraSample)
    jiraTicket['fields']['description']['content'][0]['content'][0]['text'] = "Broadband Address: " + address
    jiraTicket['fields']['summary'] = "Location Change for Customer: " + number
    jiraTicket['fields']['customfield_10034'] = issueType

    url = "https://iqvoicebot.atlassian.net/rest/api/3/issue"

    token = 'c3ViaGFqaXRnaG9zaHNnYWlydGVsQGdtYWlsLmNvbTpBVEFUVDN4RmZHRjBKaUY5VWt3WFFhQ2pveXFOSUVsZVNObmh3TktvSHdMUzlFT1VmSkRNRldUVFpkeGVLeDY2RjViX3p0amlIdGRnbWI2VUl5YThiYTVJVFBzRnRQSlhBc3JoWVhCMkg1UlZwZkpYLXpyVWo5NXFyZlNHU0hib2ZnWHoyamJLYzFTcnU5Q21nWnlvZXo4WUVCOU9FenRJR3lDREcyMlZtaF9ycE5TdXVlcmVTalU9N0JCNTY2RTY='
    headers = {
        'Authorization': 'Basic ' + token,
        'Content-Type': 'application/json'  # Adjust content type as necessary
    }
    print(jiraTicket)
    json_data = json.dumps(jiraTicket)
    print(json_data)
    # Sending a GET request to the API endpoint
    response = requests.post(url, data=json_data, headers=headers)

    # Checking if the request was successful (status code 200)
    if response.status_code == 201:
        # Parsing the JSON response
        data = response.json()

        print(data['key'])
    else:
        # Print an error message if the request was unsuccessful
        print("Error:", response.status_code)

@app.route('/jira-ticket/create', methods=['POST'])
def create_jira():
    data = request.get_json()
    customerId = data['customerId']
    description = data['description']
    issueType = data['issueType']
    transcription = data['transcription']

    address = data['address']
    number = data['number']

    new_jira_ticket = JiraDetails(customerId=customerId, description=description, issueType=issueType, transcription=transcription, jiraId=str(uuid.uuid4()))
    db.session.add(new_jira_ticket)
    db.session.commit()
    createJira(new_jira_ticket, address, issueType, number)
    # Sms api
    return jsonify({'message': 'Jira ticket created successfully'}, ), 201


@app.route('/jira-ticket/get/<int:id>', methods=['GET'])
def get_ticket(id):
    ticket = JiraDetails.query.get(id)
    if ticket:
        return jsonify({'id': ticket.id, 'description': ticket.description, 'issueType': ticket.issueType})
    else:
        return jsonify({'message': 'Ticket not found'}), 404


def createFreshdesk(new_jira_ticket, address, pincode, customer):
    freshdeskTicket = copy.deepcopy(freshDeskDTO.freshdeskSample)
    freshdeskTicket['description'] = "Broadband Address: " + address
    freshdeskTicket['subject'] = "Location Change for Customer: " + customer.number
    freshdeskTicket['email'] = customer.email

    url = "https://airtel7690.freshdesk.com/api/v2/tickets"

    token = 'ZlRDVll1UmQ3TXl4UlF4RUpSNTpY'
    headers = {
        'Authorization': 'Basic ' + token,
        'Content-Type': 'application/json'  # Adjust content type as necessary
    }
    json_data = json.dumps(freshdeskTicket)
    print(json_data)
    # Sending a GET request to the API endpoint
    response = requests.post(url, data=json_data, headers=headers)

    # Checking if the request was successful (status code 200)
    if response.status_code == 201:
        # Parsing the JSON response
        data = response.json()

        print(data['id'])
        return data['id']
    else:
        # Print an error message if the request was unsuccessful
        print("Error:", response.status_code)

def updateFreshdesk(new_jira_ticket):
    freshdeskTicket = copy.deepcopy(freshDeskDTO.freshdeskSample)
    freshdeskTicket['description'] = "Broadband Address: " + address
    freshdeskTicket['subject'] = "Location Change for Customer: " + number

    url = "https://airtel7690.freshdesk.com/api/v2/tickets"

    token = 'ZlRDVll1UmQ3TXl4UlF4RUpSNTpY'
    headers = {
        'Authorization': 'Basic ' + token,
        'Content-Type': 'application/json'  # Adjust content type as necessary
    }
    json_data = json.dumps(freshdeskTicket)
    print(json_data)
    # Sending a GET request to the API endpoint
    response = requests.post(url, data=json_data, headers=headers)

    # Checking if the request was successful (status code 200)
    if response.status_code == 201:
        # Parsing the JSON response
        data = response.json()

        print(data)
    else:
        # Print an error message if the request was unsuccessful
        print("Error:", response.status_code)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    # print(jiraDTO.jiraSample)
    # new_uuid = uuid.uuid4()
    # uuid_str = str(new_uuid)
    # print(uuid_str)
    app.run(debug=True, port=8000)



