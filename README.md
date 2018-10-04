#### TODO:
- url_for doesn't work in navigation_bar for base.html, also when using / on the backend of routes bootstrap stops working. Also is there a dynamic way to list nav links, Does nav link need active on current page?
- Use flask custom error pages
- Proper logging, get rid of logging file
- Display timer
- Indicate end of scoring
- Update scoreboard, scoreboard still there when db is gone
- Once running gray out option, enable a terminate button
- Use a better database
- Update README.md with usage and add config page images
- cause errors then catch them
- Change main.json to config
 
# Service Scoring Engine
#### Table
[Summary](#summary)

[Requirements](#requirements)

[Setup](#setup)

[Usage](#usage)

[Contributing](#contributing)

<a id="summary"></a>
### Summary
A python 3 program used to test various service uptimes for a given network infrastructure. 

<a id="requirements"></a>
### Requirements
1. Create an Ubuntu 16.04LTS outside of the firewall. An example would be the `172.31.XX.0/29` subnet on the figure below.
2. Ensure the Ubuntu 16.04LTS has internet access.
3. Setup the SSE on a Ubuntu 16.04LTS system.

<figure>
    <img src="static\images\2017Topology.png" style="border: 1px solid #000">
    <figcaption>Southeast Regional Cyber Defense Qualification Network Infrastructure</figcaption>
</figure>

<a id="setup"></a>
### Setup
1. Git clone this repository:
    - `git clone https://github.com/SilexOne/sse.git`
2. Go into the project
    - `cd sse`
3. Run the install script:
    - `./sse_setup.sh`
4. Configure the JSON file to your network:
    - Edit `scoring_engine/main.json`, see [Usage](#usage) for more details
5. Run the program:
    - `python3 main.py`
6. View the website:
    - Browse to the machine that is hosting the SSE `http://#.#.#.#`
    
<a id="usage"></a>
### Usage
1. Once installed you will need to make and configure a `scoring_engine/main.json` file. A template is already provided as `main.json.example#`, you may make a copy of `main.json.example1` as `main.json`.
    
2. View the mode's overall settings and configure if needed:
    - `logging`: This sets the logging level for SSE and how verbose the output is. It follows Python logging standard.
    - `timeframe`: This sets how long SSE will score for
    - `services`: This will hold all the service settings that `scoring_engine/services` will use.
    
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
    
    For example, logging is set at DEBUG and the test will only run for one minute. The `name` is just the title of the config itself. You can create other config files just like `main.json.example#`

3. View and configure `services`:
    - `enabled`: Determines if the SSE will score that service
    - Other Settings: Specific configuration settings to test that `services` will use

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

    For example, `dns` is enabled and the service configuration to be tested is configured as `servers` and `hostnames`. You may take a look at `services/score_dns.py` and how it uses the configuration settings.
    `ad` is disabled and will not be tested.

<a id="contributing"></a>
### Contributing
##### Service Test
If you want to test another service that isn't in SSE by default you can easily add one yourself.

1. Within `scoring_engine/main.json` add a service in `services` with the appropriate settings in both modes.

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
    
2. Create a python file based off `scoring_engine/services/template.py` and store it in the `scoring_engine/services` folder.
    - Follow the template
    - Look at existing scoring functions in `scoring_engine/services` to get real examples
    
3. Run the program and the service should be added.
    
##### Github

1.  Fork the project from github.
2.  Git clone the repository.

        $ git clone git@github.com:<YOUR_USERNAME_FOR_GITHUB>/sse.git
 
3.  Set the upstream repository.

        # Sets your git project upstream to this repository
        $ git remote add upstream https://github.com/SilexOne/sse.git

4. Ensure your fork's master mirrors the upstream repository. 
   That means you should not make any changes to your master, 
   all you need to create branches off it. You will also need to
   update your master when new changes occur in the overall project.

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
 
 5. How to merge your branch if you run into a simple merge conflict.
 
        # Updates your master branch to be the same as the upstream repository
        $ git pull upstream master
       
        # Your branch will rebase off the new master branch
        $ git rebase master new-branch-your-creating
    
 6. If your branch was merged in and you want to keep contributing.
 
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
    
        # Pretty much repeat step 4 with the changes and git add, and step 5 if applicable 
