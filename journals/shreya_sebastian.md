# Journal

## Week 1

September 5th meeting: We finalized our group and formulated ideas for our chosen system (3 hours). We discussed several ideas like an app for effecient book sharing and other ideas that leaned more towards planning and scheduling. In the end we settled on a "Smarter" home system and uploaded our problem description to Brightspace. The main idea is that the system will build upon the idea of existing smart home systems by adding a learning component. Namely, the system will be able to use data from motion sensors, light sensors, location and so on to learn routines and provide suggestions. 

## Week 2
September 10th: We decided to do weekly meetings on Mondays. During this meeting we distributed tasks for the presentation on the 12th. In the meeting, we discussed as a team what our solution direction would be and some very basic ideas for the PoC (2 hours). 

September 12th: We finalized the presentation in person together before the meeting (1 hour) with the TA and then presented it (1 hour). Some of the feedback we got was that the PoC was more about exploring a key architectural decision in our system while instead we were leaning more towards implementing a full system. 

## Week 3
September 15: We had our weekly meeting and decided on which problem analysis techniques we would like to make use of (1 hour). Additionally we did research beforehand on which techniques would best suit our use case so we could come to the meeting prepared (2 hours). We divided the techniques among ourselves and set a deadline for the 17th. I worked on the Context Analysis and also added the respective slides to the presentation (3 hours). 

## Week 4

September 22nd: We had our problem refinement meeting and got feedback that the report's structure should be improved. We also got guidance for more potential directions for our PoC. We each brainstormed and some ideas were to make use of virtual sensors and simulate data ingestion or focus on the routine suggestions aspect to validate the idea that the system can sufficiently learn using data from multiple sources. In short: Demonstrating how the system can remain available and can resync when sensors fail or disconnect (2 hours). 

## Week 5

Septermber 29th: The main subject of our meeting was to finalize the PoC direction and start working right away (1 hour 30 minutes). We explored the direction of scalability and also looked at learning routines from simulated data. But in the end, we decided to demonstrate a fault-tolerant architecture that ensures data consistency from distributed sensors, even during network failures. We then requested further feedback for this idea on Mattermost. 
October 1st: We recieved feedback on our idea. First to be explicit about what the senosrs being "available" means to us.  We also got feedback that this can be well combined with some scalability patterns. 
I worked on a PoC concept locally as it was difficult to schedule my team to meet to really finalize the PoC direction and ditribute tasks. I continued with the direction of proving system resilience during sensor failures and created a framework (2 hours). 

## Week 6

The way the PoC works is if a sensor can't connect, it stores its readings locally. Once it's back online, it sends all the saved data to a central server, which then passes the information to a processing system in an orderly way. This design is designed to handle temporary sensor outages and smooth out data flow from the sensors without losing data. To prove the concept, I built a test script that displays different phases: a period of normal operation, a simulated disconnection of a single sensor and a reconnection phase (5 hours). 
After working through some bugs, the simulation now runs successfully. It confirms that the disconnected sensor can upload its entire backlog of historical data without loss (1 hour).
I polished the PoC a bit and created a readme file (2 hours). In the report, I discussed how the different components of the PoC tackle the problems of data loss and scalability and created a simple diagram to visualise the architecture (4 hours). I also wrote a section comparing the use of different cloud models for our system (1 hour 30 minutes).

## Week 7
I updated the context analysis section to be in line with the feedback we got earlier and added a context diagram (2 hours). I also reworked the ethical implications section to be a bit less redundant and made other small edits (1 hour). 
For the PoC, I added

