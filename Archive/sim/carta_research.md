1. inspiration
    flight tracker
2. scope
    I was able to produce estimated bus arrival based on intended timetable (via gtfs files*) but it's reinventing the wheel. There are already PDFs and websites with intended bus routes/schedules. Initially i wanted to create a live tracking dashboard, displayed on e paper, to alert the bus rider how far away their bus is from their "home" bus stop.
    *GTFS is the General Transit Feed Specification, a data standard for describing public transit routes and schedules.
3. research
    I found 3 research papers (and i think all 3 came out of UTC) on carta:
    - smart city 
        - road conditions
        - weather (via DarkSky api)
        - routes
        - drivers
        - findings:
            - insufficient amount of data (bus rideship) to conclude crash predictors which is unhelpful for the "smart city" campaign
    - fuel efficiency HD EMMA (my favorite)
        - HD EMMA model development (in other words a fancy matrix to grade emission performance)
        - received ViriCiti grant which installed some instruments to collect data from 3 different kinds of buses - diesel, electric, and hybrid 
        - findings:
            - energy saving potential $49k
            - 175 metric tons of co2 reduction potential
    - optimizing routes
        - findings: 
            - condense/combine routes 
4. future directions