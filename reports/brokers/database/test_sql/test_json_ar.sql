set @json = '{
  "test": "aaa",
  "bids": [
      {
        "date": "2017-08-06T20:43:53.093560+03:00",
        "id": "a9a12503113549e8bf65a0f99267d33e",
        "selfEligible": true,
        "selfQualified": true,
        "status": "active",
        "subcontractingDetails": "",
        "tenderers": [
          {
            "address": {
              "postalCode": "03127"
            },
            "contactPoint": {
              "email": "chayka@welltex.ua",
              "telephone": "+380675575058, +380442388302"
            },
            "identifier": {
              "id": "34801840",
              "scheme": "UA-EDR",
              "uri": "http://www.welltex.ua"
            },
            "name": ""
          }
        ],
        "value": {
          "amount": 329700.77,
          "currency": "UAH",
          "valueAddedTaxIncluded": true
        }
      }
    ]
}';
    
set @len =  JSON_LENGTH(@json, "$.bids");
set @b = json_query(@json, "$.bids");
select @b;