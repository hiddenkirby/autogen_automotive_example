import autogen
import base64
from autogen.agentchat.contrib.multimodal_conversable_agent import MultimodalConversableAgent
from inventory import get_inventory, get_inventory_declaration
from mail_sender import send_mail, send_email_declaration
from flask import Flask, request, render_template

from dotenv import load_dotenv
# load environment variables from .env file
load_dotenv()

# Test Images
# https://teslamotorsclub.com/tmc/attachments/camphoto_1144747756-jpg.650059/
# https://cdn.motor1.com/images/mgl/o6rkL/s1/tesla-model-3-broken-screen.webp

# setup a Flask server (api)
app = Flask(__name__)

config_list = autogen.config_list_from_json("OAI_CONFIG_LIST")

# each agent is able to have it's own underlying language model
# in this case the damage_analyst agent can use image tools
config_list_4v = autogen.config_list_from_json(
    "OAI_CONFIG_LIST",
    filter_dict={
        "model": ["gpt-4-vision-preview"],
    },
)

llm_config = {"config_list": config_list}


def is_termination_msg(data):
    has_content = "content" in data and data["content"] is not None
    return has_content and "TERMINATE" in data["content"]


# acts as a bridge between the user and the agent
# 
# function map - only the user_proxy can execute the method 
# the inventory manager is aware of the method but doesn't execute it directly .. instead it recomments the user_proxy execute it ... then uses the results to formulate it's response
user_proxy = autogen.UserProxyAgent(
    'user_proxy',
    is_termination_msg=is_termination_msg, # checks if TERMINATE is present
    system_message="You are the boss",
    human_input_mode='NEVER',
    function_map={"get_inventory": get_inventory, "send_mail": send_mail}
)

# capable of recognizing images (using 4v)
# MultimodalConversableAgent can process images w/ GPT vision
# max_tokens increased to that i can create a detailed response
damage_analyst = MultimodalConversableAgent(
    name="damage_analyst",
    system_message="As the Damage Analyst, your role is to accurately describe the contents of the image provided. Respond only with what is visually evident in the image, without adding any additional information or assumptions.",
    llm_config={"config_list": config_list_4v, "max_tokens": 300}
)

# responsible for item availability and the price of spare parts
# is aware of the inventory database
inventory_manager = autogen.AssistantAgent(
    name="inventory_manager",
    system_message="An inventory management specialist, this agent accesses the inventory database to provide information on the availability and pricing of spare parts.",
    llm_config={"config_list": config_list, "functions": [get_inventory_declaration]})

# last step, therefor using terminate 
customer_support_agent = autogen.AssistantAgent(
    name="customer_support_agent",
    system_message="A Customer Suppport Agent, responsible for drafting and sending client emails following confirmation of inventory and pricing details specific to the brand (and damage if visible) of the car. It signals task completion by responding with 'TERMINATE' after the email has been sent.",
    llm_config={"config_list": config_list, "functions": [send_email_declaration]})

# A group chat between the agents
#    and we start with an empty messages array
groupchat = autogen.GroupChat(
    agents=[user_proxy, damage_analyst, inventory_manager,
            customer_support_agent], messages=[]
)

# chat manager agent that orchestrates group chats with multiple agents ensuring efficient comms and task distribution among them
manager = autogen.GroupChatManager(
    groupchat=groupchat, llm_config=llm_config
)

# flask root route
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        image_url = request.form['image']
        customer_email = request.form['email']
        customer_message = request.form['message']

        initiate_chat(image_url, customer_message, customer_email)

        return render_template('result.html')
    else:
        return render_template('index.html')


# initiate and give a precise process to follow
def initiate_chat(image_url, message, customer_email):
    print(f"Mail: {customer_email}")
    user_proxy.initiate_chat(
        manager, message=f"""
            Process Overview:
            Step 1: Damage Analyst identifies the car brand and the requested part (is something central, or something broken or missing) from the customer's message and image.
            Step 2: Inventory Manager verifies part availability in the database.
            Step 3: Customer Support Agent composes and sends a response email to the customer.

            Customer's Message: '{message}'
            Image Reference: '{image_url})'
            Customers Email: '{customer_email}'
        """
    )

# start the server
# This if statement line checks if the script is being run directly by the Python interpreter as opposed to being imported as a module in another script. __name__ is a special variable in Python that represents the name of the module. If the script is run directly, __name__ is set to '__main__'.
if __name__ == '__main__':
    app.run(debug=True) # When enabled, the server will reload itself on code changes, and it will also provide detailed error messages in the browser if your code raises an exception.