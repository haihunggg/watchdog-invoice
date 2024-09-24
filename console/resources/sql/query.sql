SELECT 
    "SellerTaxCode" AS "TaxCode",
    "SellerLegalName",
    Count("Id") as "SendingInvoice"
FROM 
    "MInvoice"."Invoice" 
WHERE 
    "TenantId"='?'
    AND "CreationTime" >= NOW()  - INTERVAL '12 hours'
    and "SendTaxStatus"=3
GROUP BY 
    "SellerLegalName",
    "SellerTaxCode";