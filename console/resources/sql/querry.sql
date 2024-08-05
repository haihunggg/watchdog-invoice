SELECT 
    "SellerTaxCode" AS "TaxCode",
    "SellerLegalName",
    Count("Id") as "SendingInvoice"
FROM 
    "MInvoice"."Invoice" 
WHERE 
    "TenantId"='?'
    AND "DateSign" <= NOW() - INTERVAL '6 hours'
    and "SendTaxStatus"=3
GROUP BY 
    "SellerLegalName",
    "SellerTaxCode";