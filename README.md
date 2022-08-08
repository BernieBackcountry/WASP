# 16_SPCS
> S9A created a web scraping tool to automate the lengthy, human-centric satellite pairing process used by the 16th Space Control Squadron to geolocate sources of electronic warfare jammers.
> Live demo [_here_](https://www.example.com). <!-- will post link when demo is live -->



## Table of Contents
* [General Info](#general-information)
* [Technologies Used](#technologies-used)
* [Features](#features)
* [Setup](#setup)
* [Usage](#usage)
* [Project Status](#project-status)
* [Room for Improvement](#room-for-improvement)
* [Contact](#contact)


## General Information

Operators at the 16th Space Electronic Warfare Squadron (16 SEW) use the Bounty Hunter (BH) system to monitor, detect, characterize, and geolocate sources of radiated electromagnetic energy on geostationary satellites. BH requires a pair of satellites for geolocation. This process of satellite pairing is time-intensive because operators must research satellite statistics from several websites since there is no master database. Additionally, the pair of satellites must fulfill a criteria of requirements including degrees of separation, footprint overlap, transponder overlap, frequency overlap, polarity overlap, and database entry. These requirements are achieved sequentially. Thus, if all requirements except polarity overlap are achieved, the operator must start over. This current approach involves trial and error tests to confirm a successful geolocation.

S9A created a prototype scraping tool to automate one step at a time in this satellite pairing process. Since much of the research is conducted on non-government websites housing satellite data, a web scraper provides the most immediate impact in alleviating the time operators spend scanning the various web pages for relevant data. Since many of the websites the 16th uses in their satellite pairing process are non-NIPR, non-government websites, the intent is to deploy the tool on a web application accessible from any CAC-enabled computer.

The time it takes to perform one successful satellite pair ranges from two hours to two weeks due to the strict criteria required to make a pair and the lack of a consolidated database for the satellites. Automation of this process greatly benefits the 16 SEW because it allows operators to focus on their specific, highly trained skillsets.


## Technologies Used
- Baseline web scraper tool built with Python



## Features
List the ready features here:
- Awesome feature 1
- Awesome feature 2
- Awesome feature 3


## Setup
What are the project requirements/dependencies? Where are they listed? Where is it located?

Proceed to describe how to install / setup one's local environment / get started with the project.


## Usage
How does one go about using it?
Provide various use cases and code examples here.

`write-your-code-here`


## Project Status
Project is: _in progress_ .


## Room for Improvement
Include areas you believe need improvement / could be improved. Also add TODOs for future development.

Room for improvement:
- Improvement to be done 1
- Improvement to be done 2

To do:
- Feature to be added 1
- Feature to be added 2

## Contact
SpOC/S9A analysts - Capt William McEntee (william.mcentee.2@spaceforce.mil), Lt Michelle McGee (michelle.mcgee.2@spaceforce.mil), Dr. Benjamin Johnson (benjamin.johnson.90.ctr@spaceforce.mil)


