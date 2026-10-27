// Power Query M: replace only this path parameter. Import the analysis export.
let
    Source = Csv.Document(File.Contents("C:\portfolio\PROJECT\data\processed\analysis_export.csv"),[Delimiter=",",Encoding=65001,QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source,[PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Headers,{{"observation_id",Int64.Type},{"date",type date},{"segment",type text}})
in Typed
