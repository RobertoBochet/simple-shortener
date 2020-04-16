# Simple Shortener

This is a url shortener written in python with flask

## Features

- Easily to setup
- Shortener list easily to update
- Collect daily statistics also of user-agents
- Web GUI to visualize the statistics
- Already containerized

## Installation

You can chose to run the service containerized or not.

### Docker compose 

#### Use the image on Docker Hub (recommended)

1. Download **.env** and **docker-compose.yml** files and put them in a folder.

2. Edit them to adapt the setup to your requirements(see below).

3. Run the containers.

    ```bash
    docker-compose up
    ```

#### Compile your own Docker image

1. Clone the whole repo.

    ```bash
    git clone https://github.com/RobertoBochet/simpleshortener.git ./uus
    cd uus
    ```

2. Edit the **.env** and **docker-compose.yml** to adapt the setup to your requirements(see below).

3. Build and start the containers.

    ```bash
    docker-compose build
    docker-compose up
    ```

## Configuration

You will have to provide a local or remote file in JSON format likely **example.json**.
This can be provided as local file or remote file over http(s) protocol.
You can think to versioning this file on a web service, e.g. GitLab or GitHub.

If you want to use **docker-compose** you have to edit **.env** file.

## Credits

This project is inspired by [POuL's UUS](https://gitlab.poul.org/project/uus) and it was rewritten from zero.

In this project are used the following components:

### Python modules

- [Flask](https://pypi.org/project/Flask/) (BSD License (BSD-3-Clause))
- [simplejson](https://pypi.org/project/simplejson/) (Academic Free License (AFL), MIT License (MIT License))
- [gunicorn](https://pypi.org/project/gunicorn/) (MIT License)
- [schema](https://pypi.org/project/schema/) (MIT License)
- [redis](https://pypi.org/project/redis/) (MIT License)
- [jinja2](https://pypi.org/project/Jinja2/) (BSD License)
- [requests](https://pypi.org/project/requests/) (Apache 2.0 License)
- [APScheduler](https://pypi.org/project/APScheduler/) (MIT License)

### Web components

- [Vue.js](https://vuejs.org/) (MIT License)
- [Chart.js](https://www.chartjs.org/) (MIT License)
- [Google Fonts](https://fonts.google.com/)
- [strftime for Javascript](https://hacks.bluesmoon.info/strftime/) (BSD License)