# Money Hunters
## Development team that brings product solutions to the market. 

**Our customer**: Companies or groups looking to enhance their profit margins using software solutions that increase productivity, enhance marketing strategies, or improve information organization.

**Our core prinicpal**: The development and design team should work together to satisfy the customers requirement that increases profit for the company. 

**Current product solution**: Discord-esque web application: [link](https://github.com/thegoldenmule/csci-5030/blob/main/notes/briefs/discord.md)

**Trello**: [link](https://trello.com/b/uMw7mjYG/project-management)


## To run the chat application
*Clone the repository to local machine*

*Create new enviroment* `python -m venv env`

**With in the environment** 
1. Install the required dependencies in the enivroment from [requirements.txt](https://github.com/Sathvik-Chowdary-Veerapaneni/Money_Hunters_5030_Group_Project/tree/develop/flask-discord/flaskd) 
`pip install -r requirements.txt`
2. run the `db.py` file
3. *Intialize databse* using `flask init-db` in terminal
4. from terminal change directory to flask-discord 
5. `SET FLASK_APP=flaskd`
6. `SET FLASK_ENV=development`
7. `flask run`
  



## Tests

Backend tests are ran using the module pytest and are located in the project directory `flask-discord/backend_tests`.     

To run backend tests:  
1. Install python 3.7.
2. Install the following python packages using pip: flask, flask-socketio, and pytest.  
`pip install flask flask-socketio pytest`
3. In the flask-discord directory, run:  
`python3 -m pytest backend_tests/`

TO run client tests:
1. run `python -m pytest client_tests`
