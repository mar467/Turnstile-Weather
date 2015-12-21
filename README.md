# Turnstile-Weather
For this project, I used Python to investigate the interrelationship between weather conditions in New York City and turnstile entries at the Times Square subway station. To do so, I wrangled datasets from the Weather Underground and Metro Transit Authority websites respectively.

There were two primary components to this project:

First, I used statistical methods to probe the relationship between subway ridership and various weather variables. Among my findings was that there were significantly fewer turnstile entries when skies were clear versus when skies were cloudy (p < 0.001). It appears NYC residents and commuters are less likely to take the Times Square subway when weather conditions are pleasant, suggesting they are more willing to walk to and from their destinations.

Second, I used machine learning techniques to predict the last two weeks of turnstile data at the Times Square subway station. To do this, I first applied a linear regression algorithm called gradient descent on the past year of turnstile-weather data (not including the last two weeks), managing to explain over 95% of the variance in Times Square subway ridership (R2 = .951). This high predictive power came primarily from utilizing date and time factors in the analysis, such as hour of day, day of week, and whether the day was on or near a holiday. Next, I used the obtained predictor coefficients to predict ridership for the two weeks starting on November 28th.

This code is modifiable to investigate any NYC station(s) over any time period.

More information about this project can be found in my blog post at abdulmoizrauf.wordpress.com
