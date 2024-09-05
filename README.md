# TasteTribe
**TasteTribe** is a Django web application developed by [Riccardo Vaccari](https://github.com/RiccardoVaccari) and [Andrea Monacelli](https://github.com/andreamonacelli) that represents a web portal on which users can create, explore and share recipes.
The site offers a wide range of features, including creation, editing, visualization and rating of recipes. 
To enhance your experience you can register your own account on the portal, signing up on TasteTribe allows you to create and participate to cooking-related discussions in the **Forum** sections, gathering recipes into personal **Collections** as well as exploring collections created by other TasteTribers and, lastly, create or take on exclusive cooking **Quizzes**.
Each registered user will have its own custom experience on the website thanks to the original TasteTribe Recommendation Systems that further enhances the portal exploration by suggesting recipes and collections that the user will most likely look into.
***
## Usage Instructions
### Requirements
Prior to performing any of the steps reported below, please ensure your local device satisfies the project's [requirements](https://github.com/RiccardoVaccari/TasteTribe/blob/main/requirements.txt)
### Project setup
1. **Clone the repository**:
    ```
    git clone https://github.com/RiccardoVaccari/TasteTribe.git
    cd TasteTribe
    ```
2. **Insert private key to access remote database**:
   ```
   mv /path/to/DB-PKEY .
   ```
3. **Install the required packages**
	```sh
    pipenv install
    ```
4. **Create and activate a virtual environment using Pipenv**:
    ```sh
    pipenv shell
    ```  
5. **Install Requirements**:
    ```sh
    pip3 install -r requirements.txt
    ```
6. **Launch the server**:
    ```sh
    python manage.py runserver
    ```
7. **Access the website**:
    - Through your favourite web browser go to `http://localhost:8000/`.

From here on, it is possible to explore the website as the user likes and it is possible to register your own account to the website.


## Administrator access
It is possible to access administration features by signing into the [dedicated section](http://localhost:8000/admin/) of the website using the following credentials:
|Username         |Password |
|-----------------|---------|
|tastetribe_admin |admin    |
