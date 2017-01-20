
Generating API.AI Schema
----------------------------------------
Flask-Assistant provides a command line utilty to automatically generate your assistant's intent JSON schema and register it with API.AI

This will require an existing API.AI agent, and your app should be within its own directory, as the utility will create a new folder in the app's root.

1. First obtain your agent's Developer access token from the `API.AI Console`_
2. Ensure you are in the same directory as your assistant and tore your token as an environment variable
    .. code-block:: bash
    
        export DEV_ACCES_TOKEN='YOUR ACCESS TOKEN'
3. Run the `schema` command
    .. code-block:: bash
    
        schema my_assistant.py

This will an Intent JSON object for each intent mapped to an action fucntion within your app. The Intent objects will be pushed to API.AI and create a new intent or update if an intent with the same name has already been created.

You can view the JSON generated in the newly created `schema` directory

.. note:: After running this command you may view the intents in the API.AI console. You may find that you need to add Parameters, Entities, and User Says declarations to get Intent matching working properly for your assistant, especially if it is more complex.

.. note:: Support for automatic User Says and Entities registration is coming!






.. _`API.AI Console`: https://console.api.ai/api-client/#/login