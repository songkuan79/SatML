# SatML
Data Science tools for Satellite imagery

1. Change Detection Tool: RF_Change.py
  Given a multi-temporal satellite record for a certain area, identify major 'unnatural' change sites from natural rhythms.
  Needs 4 input parameters:
  
  A. A single-date or multi-temporal image when the perceived 'change' did not occur yet
  
  B. A single-date single-band image when the perceived 'change' already took place
  
  C. A filename for the output result
  
  D. A mask file in which pixels labelled as 1 are the scope to search for change
  
