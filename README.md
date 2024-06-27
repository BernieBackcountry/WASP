# 16th EWS WASP

S9A created WASP (Web Application for Satellite Pairing), a web scraping tool to
automate thelengthy, human-centric satellite pairing process used by the 16th
Electronic Warfare Squadron to geolocate sources of electronic warfare jammers.

## Table of Contents

* [General Information](#general-information)
* [Technologies Used](#technologies-used)
* [Sources](#sources)
* [App Features](#app-features)
* [R2D2 GitLab Setup](#r2d2-gitlab-setup)
* [Local Setup](#local-setup)
* [Heroku Setup](#heroku-setup)
* [AWS CLI Setup](#aws-cli-setup)
* [Deploy Application to Heroku](#deploy-application-to-heroku)
* [Project Status](#project-status)
* [Contact](#contact)

<a name="general-information"></a>
## General Information

Operators at the 16th Electronic Warfare Squadron (16 EWS) use the Bounty Hunter
(BH) system to monitor, detect, characterize, and geolocate sources of radiated
electromagnetic energy on geostationary satellites. BH requires a pair of
satellites for geolocation. This process of satellite pairing is time-intensive
because operators must research satellite statistics from several websites since
there is no master database. Additionally, the pair of satellites must fulfill a
criteria of requirements including degrees of separation, footprint overlap,
transponder overlap, frequency overlap, polarity overlap, and database entry.
These requirements are achieved sequentially. Thus, if all requirements except
polarity overlap are achieved, the operator must start over. This current
approach involves trial and error tests to confirm a successful geolocation.

S9A proposes a web scraping tool to automate one step at a time in this
satellite pairing process. Since much of the research is conducted on
non-government websites housing satellite data, a webscraper would provide the
most immediate impact in alleviating the time operators spend scanning the
various web pages for relevant data. Since many of the websites the 16th uses in
their satellite pairing process are non-NIPR, non-government websites, the
intent is to deploy the tool on a web application accessible from any
CAC-enabled computer.

The time it takes to perform one successful satellite pair ranges from two hours
to two weeks due to the criteria required to make a pair and the lack of a
consolidated database for the satellites. Automation of this process would
greatly benefit the 16 EWS because it allows operators to focus on their
specific, highly trained skill-sets.

<a name="technologies-used"></a>
## Technologies Used

- Baseline web scraper tool built with Python
- Initial capable scraper hosted on Heroku

<a name="sources"></a>
## Sources

- [Altervista](http://frequencyplansatellites.altervista.org/) - commercial internet transponder plans (PDFs)
- [CelesTrak](http://celestrak.com/NORAD/elements/geo.txt) - TLE data
- [LyngSat](https://www.lyngsat.com/) - signals and beacon frequencies
- [Satbeams](https://www.satbeams.com/) - general information and footprints

<a name="app-features"></a>
## App Features

- Transponder Frequency PDFs
- TLE data
- Frequency
- Ku/C-band
- Beam
- EIRP
- System
- SR
- Provider Name
- Channel Name
- Channel Status
- Position
- NORAD
- Beacons
- Footprints

<a name="r2d2-gitlab-setup"></a>
## R2D2 GitLab Setup
Ensure access to the
[16th EWS R2D2 GitLab repository](https://code.levelup.cce.af.mil/ussf_analysis/16_SPCS/-/issues/48).

Register for a R2D2 account at
[https://code.levelup.cce.af.mil/users/sign_in](https://code.levelup.cce.af.mil/users/sign_in).

Once your account is registered and validated, you are able to log in via CAC authentication. If
you experience issues, reach out to the R2D2 service desk at levelup@servicenowservices.com.

### GitLab Access Token Setup

Personal access tokens are used to authenticate against Git over HTTP. They are
the only accepted password when you have Two-Factor Authentication (2FA)
enabled. When prompted for credentials, you will use your GitLab username for
username and your personal access token for password.

To obtain a personal access token, complete the following steps.
1. Log onto GitLab.
2. Click the user profile icon in the top right corner and select **Edit Profile**.
3. Select **Access Tokens** from the left side options.
4. Enter a **Token name**. (Example: r2d2-token)
5. Choose an expiration date for the token.
6. Check the relevant scopes of the token. Make sure you have read/write repository privileges.
7. Select **Create personal access token**.
8. Store your access token in a safe location. You will **not** be able to access the token once you leave the page.

### Project Setup

Pre-requisites:
- Git installation ([Download Git here](https://git-scm.com/downloads))
- (Recommended) Python IDE installation ([Example: VS Code](https://code.visualstudio.com/download))

To clone the 16_SPCS repository from R2D2 GitLab, run the following commands in a bash terminal:

1. Create and navigate to a new directory that will store the GitLab certificate:

    `mkdir Certificates`

    `cd Certificates`

2. Download the certificates:
    `echo -n | openssl s_client -showcerts -connect code.levelup.cce.af.mil:443 | sed -ne '/-BEGIN CERTIFICATE-/,/-END CERTIFICATE-/p' > r2d2_gitlab_certificate.crt`
3. Configure Git to use the certificates:
    `git config --global http.sslCAInfo <full path to certs>/Certificates/r2d2_gitlab_certificate.crt`
4. Configure Git to store login credentials for a specified amount of seconds:
    `git config --global credential.helper "cache --timeout=<timeout>"`
5. Configure Git to store the user's identity:
    `git config --global user.email "<user's email address>"`
    `git config --global user.name "<user's name>"`
6. Navigate back to the main directory:
    `cd ..`
7. Create and navigate to a new directory that will store the GitLab projects:
    `mkdir PROJECTS`
    `cd PROJECTS`
8. Clone the repository. Input user credentials when prompted:
    `git clone https://code.levelup.cce.af.mil/ussf_analysis/16_SPCS.git`

<a name="local-setup"></a>
## Local Setup
Ensure Python is version 3.7.

Within the terminal:

1. Navigate to the project directory:

    `cd <path to 16_SPCS>`

2. Create a new virtual environment:

    `python -m venv <virtual environment name>`

3. Activate the virtual environment:
    - bash: source

        `<virtual environment name>/bin/activate`

    - Git Bash:

        `source <virtual environment name>/Scripts/activate`

    - cmd.exe:

        `<virtual environment name>\Scripts\activate.bat`

    - PowerShell:

      `<virtual environment name>\Scripts\Activate.ps1`

4. Install the necessary packages:

    `pip install -r requirements.txt`

5. Run the application locally:

    `python -m wasp_tool_dash.app`

<a name="heroku-setup"></a>
## Heroku Setup

Pre-requisites (in order):
1. Git installation ([Download Git here](https://git-scm.com/downloads))
2. First-time Git setup ([Helpful Documentation](https://git-scm.com/book/en/v2/Getting-Started-First-Time-Git-Setup))
3. Heroku CLI installation ([Download Heroku CLI here](https://devcenter.heroku.com/articles/heroku-cli#install-the-heroku-cli))

<a name="aws-cli-setup"></a>
## AWS CLI Setup

Download the [AWS CLI](https://aws.amazon.com/cli/).

Helpful terminal commands:
  - Configure the bucket:

      `aws configure`

  - View bucket files recursively:

      `aws s3 ls -r s3://<BUCKETEER_BUCKET_NAME>`

  - Delete bucket files recursively:

      `aws s3 rm -r s3://<BUCKETEER_BUCKET_NAME>`

<a name="deploy-application-to-heroku"></a>
## Deploy Application to Heroku

After cloning the 16_SPCS repository, within the terminal:

1. Login to Heroku:

    `heroku login`

2. Set environmental variables:

    - `export AWS_ACCESS_KEY_ID=<BUCKETEER_AWS_ACCESS_KEY_ID>`

    - `export AWS_SECRET_ACCESS_KEY=<BUCKETEER_AWS_SECRET_ACCESS_KEY>`

    - `export S3_BUCKET_NAME=<BUCKETEER_BUCKET_NAME>`

3. Add files in working directory:

    `git add .`

4. Initial commit:

    `git commit -m "intial commit"`

5. Deploy app to Heroku:

    `git push heroku master`

<a name="project-status"></a>
## Project Status
Project status: _prototype delivered_ . Prototype web scraping tool complete. Initial functionality achieved.

<a name="contact"></a>
## Contact
SpOC/S9A analysts - Lt Michelle McGee (michelle.mcgee.2@spaceforce.mil), Lexi Denhard (alexis.denhard.ctr@spaceforce.mil)
