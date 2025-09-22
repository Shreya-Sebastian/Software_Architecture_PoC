# Report

Authors: Wout Burgers, Levi Raktoe, Shreya Sebastian, Archita Selvam

# Smarter home.

The goal of the Smarter Home is to make home automation transparent and accessible, especially for those with less technical expertise. Existing home automation systems allow users to control and automate their homes with an incredible degree of freedom. However, not all users have the technical knowledge to fully make use of this freedom. The Smarter Home addresses this problem through transparent data usage, intuitive interfaces and data-driven automation suggestions. With those features, users of all backgrounds will be able to confidently automate their home.

## Scenarios

The user will interact with the Smarter Home in a way similar to current home automation systems:

**Device pairing:** The user connects a device connects to the Smarter Home, allowing its sensor data to be read by the system, and allowing the Smarter Home to control it.

**Device control**: The user may control devices through the system.

**Authorisation levels**: A user restricts access to the system, certain devices, or recorded data for another user.

**Add automation**: The user creates some kind of automation.

**Additionaly, the Smarter Home system will have the following features**:

**Action recording**: The system records sensor data and the user's commands. The data is annotated with the time, device and type (user command / sensor data).

**Viewing recorded data and routines**: The user views the recorded data & identified routines. They can be sorted based on annotations.

**Routine identification**: The system processes the data to identify routines based on both or either:

- Specific actions repeatedly happening in a certain order.
- Specific actions repeatedly happening at a specific moment.

**Automation suggestion**: The system suggests automations to the user based on identified routines.

## Key Quality Attributes

**Privacy**: Recorded data is not immediately sensitive but should still be unavailable outside the system. Full transparency on what data is recorded.

**Correctness**: The system recommends useful automations. An automation is useful when it operates devices in a way a user already does manually, or in a way a user would, given the choice.

**Usability**: One of the goals of the Smarter Home is to be as accessible as possible. To achieve this goal, user interfaces must be simple and intuitive. Recommendations must show what information they're based on, so that the system can be trusted by technical and non-technical people alike.

**Security**: Only authenticated users and devices should be able to access the system to view its recorded data or operate its devices.

**Availability**: The system should not fail when any of its devices fail, and its devices should not be unusable if the system fails.

**Extensibility**: New types of sensors enter the market all the time. On a longer timescale, these devices may provide new types of data. To make sure our system can continue to offer accurate automation recommendations, our system must be readily extensible to support new devices and types of data.

### Privacy vs. Correctness

Privacy is a main concern with smart home systems, due to the large amounts of data IoT sensors collect inside users' homes. This data might not be immediately sensitive, but can present security concerns in aggregate. The routines can only be accurately identified based on accurate data, and privacy is therefore a direct tradeoff with the correctness of the system. By being completely transparent about the data collected, and allowing the user to inspect this data, they are empowered to make a more informed decision about the data they want recorded and or stored.

### Security

Security is a key concern for smart home systems in general. Firstly, this is because the risk involved: the loss of privacy or the loss of control over the devices in ones own home. Secondly, smart home systems are more vulnerable to cyberattacks due to their distrubuted, heterogeneous nature: all devices must be secure, otherwise they may form a gateway to the rest of the system. Additionally, the system is always active all the time and therefore always a possible target.

#### Security vs. Extensibility

As every device connected to the system is an avenue for attack, constraints need to be placed on what devices may access the Smarter Home. This means that devices may enter the market that cannot be supported without compromising security. To make sure our goals regarding security and thereby privacy and availability are met we can only allow connections with devices that are considered secure.

# Context Analysis

A thorough context analysis is essential to understand the factors influencing the **“Smarter Home System”** project and to identify areas that must be managed for successful implementation. The system’s goals are to simplify home automation by learning routines from inhabitants, suggesting useful automations, and tailoring automation to different roles.

The smart home market is rapidly expanding, with increasing demand for automation and energy efficiency (Technavio, 2023). From a user perspective, current systems often present two issues: users are unsure of what automations they truly want, and the learning curve for implementing these automations can be steep (Intille et al., 2019). Addressing these challenges requires not only intuitive system design but also robust underlying infrastructure.

The effectiveness of such solutions depends heavily on the accuracy and integration of sensors and connected devices. At the same time, privacy and security concerns are large, as home data is inherently personal and sensitive. Additionally, regulatory frameworks such as the EU’s GDPR require strict safeguards around data use and storage (GDPR Advisor, 2023).

---

## External Risks

A number of risks emerge from this external context:

- **Privacy and Security Concerns**: Personal data could be vulnerable to breaches or unauthorized use (Liu et al.).
- **User Adoption**: If the system proves overly complex or fails to establish trust, potential users may hesitate to engage with it (Fischer et al.).
- **Technological Challenges**: Risks include unreliable machine learning outcomes, sensor inaccuracies, and difficulties ensuring seamless integration with diverse ecosystems (Wang et al.).
- **Over-Automation**: Incorrect assumptions about user routines could lead to frustration or disengagement (Fischer et al.).
- **Service Reliability**: Dependency on continuous internet connectivity or cloud services introduces the possibility of service interruptions (Liu et al.).
- **Regulatory Changes**: The evolving nature of data protection laws and smart home standards requires adaptability (Alshammari and Simpson).

---

## Dependencies

The successful development and deployment of the **Smarter Home System** rely on several critical dependencies:

1. **Hardware and Sensors**  
   The system's effectiveness hinges on the accurate functioning of various smart home devices, including motion sensors, smart lights, thermostats, security cameras, and other IoT devices. Inaccuracies or failures can compromise the system’s ability to learn routines and suggest meaningful automations.

2. **Software Integration**  
   The system must integrate seamlessly with multiple smart home platforms (e.g., Apple HomeKit, Google Home, Amazon Alexa) and device protocols (Zigbee, Z-Wave, Wi-Fi). Compatibility issues could limit effectiveness or adoption (OECD, 2018).

3. **Machine Learning and Data Analytics**  
   AI-driven suggestions rely heavily on robust machine learning algorithms that can accurately recognize patterns in user behavior and generate useful automations. This requires continuous access to high-quality data from user interactions and connected devices.

4. **Cloud Services and Connectivity**  
   Many features, including real-time suggestions, routine learning, and remote access, depend on stable internet connectivity and cloud infrastructure. Outages or latency issues could reduce system reliability and user satisfaction (Moldstud, 2023).

5. **Regulatory Compliance**  
   Compliance with data protection and privacy regulations (such as GDPR) is essential. The system depends on legal frameworks for data storage, processing, and consent management, which must be continually monitored as regulations evolve (Office of the Victorian Information Commissioner, 2023).

6. **User Engagement and Feedback**  
   The system’s AI requires ongoing user interactions to refine its suggestions and adapt to individual preferences. Adoption and sustained engagement depend on intuitive interfaces, clear benefits, and user trust (Zigpoll, 2023).

7. **Maintenance and Updates**  
   Continuous software updates, bug fixes, and security patches are essential for the system to remain functional and secure. Dependency on a structured maintenance plan is critical to prevent obsolescence or vulnerabilities (OECD, 2018).

---

# Stakeholder Analysis

The proposed smart home system is designed to observe and learn the daily routines of household inhabitants. We want to use these insights to suggest suitable automations. Unlike existing solutions this system reduces barriers by recommending where automation could make the difference. It combines two main things. The extensibility with a wide range of sensors and also the ability to manage differentiated user access. This is done to ensure that the different roles, such as adults and kids, will only interact with the appliances that are relevant to them. To be able to fully understand the opportunities and challenges of the system, it is essential to conduct a stakeholder analysis on the system.

The primary stakeholders are the homeowners and adult residents. These are the main users of the system and their interests are in the convenience, the comfort and the efficiency. They are the most likely to value a home that takes over the repetitive tasks. These tasks could include actions such as switching off lights and locking doors, and also adjusting thermostats. Many people will like the potential for energy savings and the cost reductions. However this group is also the most vulnerable to concerns over their privacy. The system records routines, and it could reveal sensitive information about when people are just at home. But also when they sleep or when they leave the house. If this is not handled correctly such data could become a security risk. Furthermore some users may fear losing control over their home environment if the system over-automates or offers any suggestions that might feel intrusive. Their experience will determine in the end whether the system is accepted and whether it can be integrated into the everyday life.

Secondary users, such as children guests or tenants are less involved in the decision making but are still important to the system. They require user interfaces that are safe and simple. The access should also be restricted to only those parts of the home relevant to them. For example, a child should be able to control the lights in their own bedroom but they should not the household heating system. Guests or temporary tenants may like the convenience of automated living. But it could also feel uneasy about being monitored if they are being inside someone else their smart home. This system negatively impact the overall satisfaction of their stay.

Another import group of stakeholders to think about consists of the system developers and technology providers. Their role is to ensure the technical robustness of the platform. Particularly in integrating the sensors and devices from different brands. They also carry responsibility for designing the machine learning models that detect the user routines. Developers should go for a balance between personalization and privacy. Also compatibility with existing platforms such as Google Home, Amazon Alexa or Apple HomeKit will be essential to make the system a success.

Manufacturers of smart appliances and sensors represent another stakeholder group. Their interest lies in ensuring that their products integrate seamlessly with the proposed system. This can also then boost the sales of the smart home products. At the same time, some manufacturers may fear that they are being overshadowed or locked out if the system privileges for certain brands. Whether the system uses open standards and API’s, will also determine the reach of the system and the amount of systems and homes that are able to use the system.

Data protection authorities are also implicated. Given that the system collects sensitive personal data about household routines, it will have to comply with the regulations. These are regulations such as the General Data Protection Regulation in Europe or the California Consumer Privacy Act in the United States. Additional stakeholders can include the utility providers and the energy companies, who may see some opportunities in collaboration with the system. For example data on energy consumption could reduce the environmental impact of the household. Similarly insurers and real estate stakeholders are interested because smart homes can reduce risks such as fire or flooding. This can increase the value of the home.

Throughout these stakeholders, there exist potential conflicts. Personalization and privacy are a difficult topic. Residents might want intelligent and customized automation, but governments require tight restrictions to look after personal data. Developers may want the open interoperability, but competitors resist sharing their technologies to protect the business space.

In conclusion, the smart home system has significant potential to make automation available to mass consumers on a more affordable basis through reduced learning needs and smart recommendations. Its stakeholders are homeowners and residents on one hand and developers, manufacturers, regulators and even insurers on the other hand. Each group has its own interests and frictions and through well designed transparency and stakeholder engagement, the system can provide benefit to all of the people that are related to it.

# Ethical Implications and Mitigations

Although smart homes offer benefits like convenience and efficiency, they also pose considerable ethical issues such as how the data recorded from the user is stored and used. They raise several privacy and security concerns some of which would be addressed in this project.

A major ethical concern posed by smart homes is privacy. The fundamental operative principle behind smart homes is analyzing user data to identify patterns of user behavior and suggest automation solutions to reduce user effort. However, this would automatically involve constantly monitoring and recording user data, which in turn would result in the increased risk of surveillance by a third party. Since this data has to be stored, it could become the target for potential misuse by unscrupulous elements. Sensitive personal data could be used to target the user for profiling, advertising or manipulation. Therefore the software architecture has to necessarily anticipate this ethical concern and build preemptive solutions into the construction of the smart home. One possible solution could involve providing the user with the choice to make decisions on whether the data can be stored or not. Yet another solution could be and having sensitive data stored and processed locally rather than in cloud. Also the data stored can be made accessible to the user themselves rather than to third parties. It is also essential to collect only mandatory data for functionality to maintain privacy.

Another major concern that smart homes pose is that the smart devices in smart homes are vulnerable and prone to hacking. The user's lack of awareness of cybersecurity practices often lead to smart homes being exposed to potential hacking threats. In order to have a secure smart home, sensitive data need to be encrypted during transit and rest. Sensitive data can be stored in separate databases in local hubs. The system can also be implemented using role-based access control where each microservice accesses only what it needs. Security protocols can also be used when handling data. Another measure that can be taken is using the daily device usage blueprint to track any irregular practices to identify a third-party and alerting the user through alarms, and other smart devices, lock the functions of the devices and also have emergency line alerted.

Another ethical concern posed by smart homes is subtle and not as overt as the security issues. This is related to the long-term physical and psychological impact of smart homes on the user. Living in smart homes ultimately leads to the gradual reduction of human autonomy and control. The user slowly begins to depend on the smart devices and loses the functionality of his / her own innate thinking and decision-making capabilities. This can best be addressed by providing the user with the choice to automate a task. The user can make an informed decision rather than being unconsciously manipulated to surrender to the convenience of automation. The user can also have the choice to de-automate any task at any time. The system can be made consultative and interactive to inform the user of potential risks and provide agency to the user to make the final decision regarding permitting automation.

Yet another concern that smart homes raise is that they create a digital divide. The use of advanced technology in smart homes can often overwhelm individuals who are not comfortable with complex technology. Disabled individuals and the elderly might find it hard to use the features of a smart home as it may be too sophisticated and is not inclusive in its design. To mitigate this, the system can incorporate a multi-modal system of operation where a combination of voice commands, textual commands and even gestures and movements can be used to activate the smart devices so that it may benefit people with different kinds of disability.

## References

- Technavio. _Smart Home Market to Grow by USD 255.2 Billion, 2025–2029: Rising Consumer Interest in Home Automation Drives Growth; Report on How AI Is Redefining Market Landscape._ PR Newswire, 2023. [Link](https://www.prnewswire.com/news-releases/smart-home-market-to-grow-by-usd-255-2-billion-2025-2029-rising-consumer-interest-in-home-automation-drives-growth-report-on-how-ai-is-redefining-market-landscape---technavio-302362885.html)

- Intille, Stephen, et al. _He’s Safe, but I’m Not: User Challenges in End-User Programming of Smart Home Devices._ Journal of Human–Computer Interaction, vol. 35, no. 14, 2019, pp. 1234–1256. [PDF](https://homes.cs.washington.edu/~jessejm/data/HeSafeThings2019.pdf)

- GDPR Advisor. _GDPR and Smart Home Data: Securing Connected Devices and User Privacy._ GDPR-Advisor.com, 2023. [Link](https://www.gdpr-advisor.com/gdpr-and-smart-home-data-securing-connected-devices-and-user-privacy/)

- Alshammari, Zainab, and Andrew Simpson. _A Scoping Review: Smart Home Privacy._ SCITEPRESS – Science and Technology Publications, 2024. [Link](https://www.scitepress.org/Papers/2024/122559/122559.pdf)

- Fischer, Jesse, et al. _When Smart Devices Are Stupid: Negative Experiences Using Home Devices._ Proceedings of the 2019 Workshop on Usable Security (USEC), 2019. [PDF](https://homes.cs.washington.edu/~jessejm/data/HeSafeThings2019.pdf)

- Liu, Yang, et al. _The Digital Harms of Smart Home Devices: A Systematic Literature Review._ arXiv preprint arXiv:2209.05458, 2022. [arXiv](https://arxiv.org/abs/2209.05458)

- Wang, Ming, et al. _Automation Configuration in Smart Home Systems._ arXiv preprint arXiv:2408.04755, 2024. [arXiv](https://arxiv.org/abs/2408.04755)

- Moldstud. _Best Practices for Cloud-Based Smart Home IoT Development._ Moldstud, 2023. [Link](https://moldstud.com/articles/p-top-best-practices-for-smart-home-iot-application-development-on-cloud-platforms)

- Office of the Victorian Information Commissioner. _Internet of Things and Privacy – Issues and Challenges._ OVIC, 2023. [Link](https://ovic.vic.gov.au/privacy/resources-for-organisations/internet-of-things-and-privacy-issues-and-challenges/)

- OECD. _Consumer Policy and the Smart Home._ OECD, 2018. [Link](https://www.oecd.org/content/dam/oecd/en/publications/reports/2018/04/consumer-policy-and-the-smart-home_5cd05699/e124c34a-en.pdf)

- Zigpoll. _How Data Scientists Improve User Interaction Insights for Smart Home Devices to Make Everyday Tasks More Intuitive._ Zigpoll, 2023. [Link](https://www.zigpoll.com/content/how-can-a-data-scientist-help-improve-user-interaction-insights-for-our-smart-home-devices-to-make-everyday-tasks-more-intuitive)
