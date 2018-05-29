# CloudXperiment

Robust online experiment runner, utilising the cloud to allow 1000s of concurrent participants.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project to amazon cloud.

### Prerequisites

What things you need to install the software and how to install them

```
Python 3.6
```

### Installing on your local system

A step by step series of examples that tell you how to get a development env running

```
1. Download the project from github and extract contents (eg on windows, to C:\Users\your_user_name\XperimentCloudDemo).

2. virtualenv VENV
do this in the top directory, eg, C:\Users\your_user_name\XperimentCloudDemo, creating a virtualenvironment.

3. cd VENV. cd Scripts. activate.bat
activating virtual environment. Then return to the top directory.

4. pip install -r xperiment/requirements.txt
can take a few minutes.

5. AWS CONFIGURE
you will need you amazon cloud key and secret I strongly advise creating IAM credentials and not using your admin creds.

6. python manage.py shell -c "from django.core.management import utils; print(utils.get_random_secret_key())"
We are creating a salt which is used for randomisation in Django. Copy the long sequence

7. Rename xperiment/zappa_settings_DEMO.json to xperiment/zappa_settings.json.

8. Edit this file. for DJANGO_SECRET_KEY, use the long sequence you generated in step 6.

9. python manage.py migrate

10. python manage.py createsuperuser

11. python manage.py runserver

12. in your browser, navigate to http://127.0.0.1:8000/. With any luck, it is working.
```

Let's

```
until finished
```

End with an example of getting some data out of the system or using it for a little demo

## Running the tests

Explain how to run the automated tests for this system

### Break down into end to end tests

Explain what these tests test and why

```
Give an example
```

### And coding style tests

Explain what these tests test and why

```
Give an example
```

## Deployment

Add additional notes about how to deploy this on a live system

## Built With

* [Dropwizard](http://www.dropwizard.io/1.0.2/docs/) - The web framework used
* [Maven](https://maven.apache.org/) - Dependency Management
* [ROME](https://rometools.github.io/rome/) - Used to generate RSS Feeds

## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags).

## Authors

* **Billie Thompson** - *Initial work* - [PurpleBooth](https://github.com/PurpleBooth)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Hat tip to anyone whose code was used
* Inspiration
* etc
