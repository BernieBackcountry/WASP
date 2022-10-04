# 16_EWS
> S9A created a web scraping tool to automate the lengthy, human-centric satellite pairing process used by the 16th Electronic Warfare Squadron to geolocate sources of electronic warfare jammers.
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

Operators at the 16th Electronic Warfare Squadron (16 EWS) use the Bounty Hunter (BH) system to monitor, detect, characterize, and geolocate sources of radiated electromagnetic energy on geostationary satellites. BH requires a pair of satellites for geolocation. This process of satellite pairing is time-intensive because operators must research satellite statistics from several websites since there is no master database. Additionally, the pair of satellites must fulfill a criteria of requirements including degrees of separation, footprint overlap, transponder overlap, frequency overlap, polarity overlap, and database entry. These requirements are achieved sequentially. Thus, if all requirments except polarity overlap are achieved, the operator must start over. This current approach involves trial and error tests to confirm a successful geolocation.

S9A proposes a web scraping tool to automate one step at a time in this satellite pairing process. Since much of the research is conducted on non-government websites housing satellite data, a web scraper would provide the most immediate impact in allievating the time operators spend scanning the various web pages for relevant data. Since many of the websites the 16th uses in their satellite pairing process are non-NIPR, non-government websites, the intent is to deploy the tool on a web application accessible from any CAC-enabled computer.  

The time it takes to perform one successful satellite pair ranges from two hours to two weeks due to the criteria required to make a pair and the lack of a consolidated database for the satellites. Automation of this process would greatly benefit the 16 EWS because it allows operators to focus on their specific, highly trained skillsets.



## Technologies Used
- Baseline web scraper tool built with Python

## Sources
- [Satstar](http://satstar.net/satellites.html) - links to footprints
- [Satstar BeamFinder](http://satstar.net/setup.html) - find beams over given location
- [LyngSat](https://www.lyngsat.com/) - signals and beacon frequencies
- [AlterVista](http://frequencyplansatellites.altervista.org/) - commercial internet transponder plans (PDFs)
- [CelesTrak](http://celestrak.com/NORAD/elements/geo.txt) - TLE data
- [DishPointer](https://www.dishpointer.com) - calculating pointing angles



## Features
List the ready features here:
- Data tables from satstar, lyngsat, and celestrak
- Consolidated pdf master file of transponder plans from celestrak


## Setup
What are the project requirements/dependencies? Which web sources are NIPR accessible vs non-NIPR accessible?

Proceed to describe how to install / setup one's local environment / get started with the project.


## Usage
What is the user interface for this tool (dashboard, web-based application, NIPR VAULT, Microsoft Power App via a Teams channel, Microsoft Teams page where S9A posts updated data, etc)? What is the ideal time interval for re-running the tool and delivering updated "master data"? 

Provide various use cases and code examples here.

`write-your-code-here`


## Project Status
Project is: _in progress_ . Prototype web scraping tool complete.


## Next Steps

To do:
- Understand deployment needs and environment
- Deploy IOC tool
- User Testing/Validation on IOC tool
- Improve IOC tool to deliver FOC tool

## Contact
SpOC/S9A analysts - Capt Jeff Williams (jeffrey.williams.51@spaceforce.mil), Lt Michelle McGee (michelle.mcgee.2@spaceforce.mil), Dr. Benjamin Johnson (benjamin.johnson@contemplasolutions.com), Lexi Denhard (alexis.denhard.ctr@spaceforce.mil)


