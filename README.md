### Liine Take Home 

__Python is preferred, but if you feel unable to complete it using python, use whatever programming language you feel most comfortable in.__

Build an API with an endpoint which takes a single parameter, a datetime string, and returns a list of restaurant names which are open on that date and time. You are provided a dataset in the form of a CSV file of restaurant names and a human-readable, string-formatted list of open hours. Store this data in whatever way you think is best. Optimized solutions are great, but correct solutions are more important. Make sure whatever solution you come up with can account for restaurants with hours not included in the examples given in the CSV. Please include all tests you think are needed.

### Assumptions:
* If a day of the week is not listed, the restaurant is closed on that day
* All times are local — don’t worry about timezone-awareness
* The CSV file will be well-formed, assume all names and hours are correct

### Want bonus points? Here are a few things we would really like to see:
1. A Dockerfile and the ability to run this in a container

If you have any questions, let me know. Use git to track your progress, and push your solution to a github repository (public or if private just give me access @sharpmoose)



# TODO

1. Finish Readme
1. Create a docker setup
1. Add more error handling
1. Add tests
1. Maybe ask more about what they mean about the handling all the hours.
    1. But I think my logic should hold up either way.


# Decisions

* I went with a separate parse data setup and saved to csv (might change to postgres for docker version)
* Used pandas because I am a data person and grew up with it. There are other options.
* Used uv as my package manager. Been exploring it a bunch lately.
* Went with FastAPI because for this style of project it is just faster to get running.
* 