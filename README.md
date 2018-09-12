#### TODO:
- Proper logging
- Logging to WEB UI
- Global Variables like scoring, and data. Better way?
- having two programs use a database and know the location

# Service Scoring Engine
#### Table
[Summary](#summary)

[Setup](#setup)

[Usage](#usage)

[Contributing](#contributing)

<a id="summary"></a>
### Summary
A python 3 program used to test various service uptimes for a given network infrastructure. 

<a id="setup"></a>
### Setup
1. Git clone this repository:
    - `git clone https://github.com/SilexOne/ise.git`
2. Run the install script:
    - `./sse_setup.sh`
3. Configure the JSON file to your network:
    - The `main.json` chooses if your testing or actually scoring your services and enables which ones you want to use.
4. Run the program:
    - `python main.py`
5. View the website:
    - Browse to the machine that is hosting the SSE `http://#.#.#.#`.
    
<a id="usage"></a>
### Usage
1. Once installed you will need to make and configure a `main.json` file. A template is already provided as `main.json.example#`, you may make a copy of `main.json.example1` as `main.json`.
    
2. View the mode's overall settings and configure if needed:
    - `logging`: This sets the logging level for SSE and how verbose the output is. It follows Python logging standard.
    - `timeframe`: This sets how long SSE will score for
    - `services`: This will hold all the service settings that `services` will use.
    ```
     {
        "name": "testing",
        "logging": "DEBUG",
        "timeframe": {
          "hours": "0",
          "minutes": "1"
        },
        "services": {
            ...
     }
    ```
    For example, logging is set at DEBUG and the test will only run for one minute. The `name` is just the title of the config itself. You can create other config files just like `main.json.example#`

3. View and configure `services`:
    - `enabled`: Determines if the SSE will score that service
    - Other Settings: Specific configuration settings to test that `services` will use
    ```
    {
    "name": "testing",
    "logging": "DEBUG",
    "timeframe": {
      "hours": "0",
      "minutes": "1"
    },
    "services": {
      "dns": {
        "enabled": "1",
        "servers": {
          "main": "8.8.8.8",
          "secondary": "8.8.4.4"
        },
        "hostnames": {
          "wcsc.usf.edu": "131.247.1.113",
          "webcse.csee.usf.edu": "131.247.3.5"
        }
      },
      "ad": {
        "enabled": "0"
      },
    }
    ```
    For example, `dns` is enabled and the service configuration to be tested is configured as `servers` and `hostnames`. You may take a look at `services/score_dns.py` and how it uses the configuration settings.
    `ad` is disabled and will not be tested.

<a id="contributing"></a>
### Contributing
##### Service Test
If you want to test another service that isn't in SSE by default you can easily add one yourself.
1. Within `main.json` add a service in `services` with the appropriate settings in both modes.
    ```
    {
        "name": "production",
        "logging": "INFO",
        "timeframe": {
          ...
        },
        "services": {
          "dns": {
            ...
          },
    ----> "YOUR_SERVICE_NAME": {
    ---->   "enabled": "1",
    ---->   "SETTINGS_USED_IN_THE_PYTHON_FILE": "something"
          },
          ...
        }
    }
    ```

2. Create a python file based off `services/template.py` and store it in the `services` folder.
    - Follow the template guidelines
    - Import the necessary libraries, `from utils.settings import data, collect`
    - Ensure the decorator is on your function, `@collect(data.get('services').get('YOUR_SERVICE_NAME_YOU_CREATED_IN_THE_JSON_FILE').get('enabled'))`
    - Use the settings from the json to test your service, This will be passed in as a parameter `def A_NAME_THAT_PERTAINS_TO_YOUR_SERVICE_TEST(config):`, then can be used as so `service_settings = config.get('services').get('YOUR_SERVICE_NAME_YOU_CREATED_IN_THE_JSON_FILE')`
    - Return either a 1 or 0 which represent PASS/FAIL
    - Look at existing scoring functions in `services` to get real examples
    
3. Run the program and the service should be added.
    
##### Github
1.  Fork the project from github.
2.  Git clone the repository.

    ```bash
    $ git clone git@github.com:<YOUR_USERNAME_FOR_GITHUB>/ise.git
    ```
 
3.  Set the upstream repository.

    ```bash
    # Sets your git project upstream to this repository
    $ git remote add upstream https://github.com/SilexOne/ise.git
    ```

4. Ensure your fork's master mirrors the upstream repository. 
   That means you should not make any changes to your master, 
   all you need to create branches off it. You will also need to
   update your master when new changes occur in the overall project.
   
   ```bash
   # Updates your master branch to be the same as the upstream repository
   # Run this specific command everytime the upstream repository changes
   $ git pull upstream master
   
   # Show which branch you are on
   $ git branch
   * master

   # Create a new branch and use it
   $ git checkout -b new-branch-your-creating
   
   # Verify you are using that new branch
   $ git branch
     master
   * new-branch-your-creating

   # Make changes and add to the project
   
   # Add and commit the new changes
   $ git add .
   $ git commit - m "your commit message"

   # Push your branch to your github
   $ git push origin new-branch-your-creating

   # Go to github and do a pull request
   # Then wait for it to be merged in or denied
   ```
 
 4. How to merge your branch if you run into a merge conflict.
 
    ```bash
    # Updates your master branch to be the same as the upstream repository
    $ git pull upstream master
   
    # Your branch will rebase off the new master branch
    $ git rebase master new-branch-your-creating
    ```
    
 5. If your branch was merged in and you want to keep contributing.
 
    ```bash
    # Updates your master branch to be the same as the upstream repository
    $ git pull upstream master

    # Switch back to master
    $ git checkout master

    # Verify you are on master
    $ git branch
    * master
      new-branch-your-creating

    # Branch off master
    $ git checkout -b another-branch-you-created

    # Verify you are on that branch
    $ git branch
      master
      new-branch-your-creating
    * another-branch-you-created

    # Pretty much repeat step 3 with the changes and git add, and step 4 if applicable 
    ```
