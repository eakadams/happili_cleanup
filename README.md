# happili_cleanup
Clean up Apercal files on happili

September 2022: Have expanded for 
:
- a full selfcal cleanup (keep zipped models of lest seflcal and vis only)
- Keep final continuum images and residuals, compress masks and models
- Remove calibrator vis (previously done manually)

NOTE! This can take a while to run, so best to do in a screen.

Current data usage (8 Sep 2022):
- tank1: 25T / 97%
- tank2: 25T / 97%
- tank3: 25T / 97%
- tank4: 25T / 96%
- data1: 30T / 92%
- data2: 31T / 94%
- data3: 30T / 92%
- data4: 32T / 95%

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

Failed to run on taskids: