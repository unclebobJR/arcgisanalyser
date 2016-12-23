# arcgisanalyser

Dit draait standalone, maar kan ook als AWS Lambda draaien, als volgt:

Vanuit de master, maak een archive (dus zonder .git)
git archive --format zip --output "arcgisanalyser.zip" master

Vervolgens upload deze naar een bestaande lambda function
aws lambda update-function-code --function-name arcgisanalyser --zip-file fileb://c:/dev/ArcGisAnalyser/arcgisanalyser.zip

