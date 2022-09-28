# happili_cleanup
Clean up Apercal files on happili

September 2022: Have expanded for 
:
- a full selfcal cleanup (keep zipped models of lest seflcal and vis only)
- Keep final continuum images and residuals, compress masks and models
- Remove calibrator vis (previously done manually)

NOTE! This can take a while to run, so best to do in a screen.

Current data usage (15 Sep 2022, 14:35):
- tank1: 18T / 69%
- tank2: 18T / 70%
- tank3: 19T / 71%
- tank4: 18T / 71%
- data1: 30T / 89%
- data2: 30T / 92%
- data3: 29T / 87%
- data4: 28T / 85%

Data usage before expanded cleanup (6 Sep 2022):
- tank1: 26T / 100%
- tank2: 26T / 100%
- tank3: 26T / 100%
- tank4: 26T / 100%
- data1: 31T / 93%
- data2: 32T / 97%
- data3: 31T / 95%
- data4: 31T / 93%

Start cleanup, run on dates:
- 190701 - 190731
- 190801 - 190831
- 190906
- 190907 - 190930
- 191001 - 191231 
- 200101 - 200630 
- 200701 - 201231 

Failed to run on taskids (think these are files in apercal group; asked to be added to that group):
- 200406054
- 200427042
- 210229084
- 200622045 - 200624213
- 200929094
- 200930045
- 200912042
- 200913041
- 201029084
