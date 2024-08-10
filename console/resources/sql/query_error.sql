SELECT 
    "SellerTaxCode" AS "TaxCode",
    "SellerLegalName",
    Count("Id") as "SendingInvoice"
FROM 
    "MInvoice"."Invoice" 
WHERE 
    "TenantId"='?'
    AND "CreationTime" BETWEEN 'checkpoint' and (NOW() + INTERVAL '7 hours')
    and "SendTaxStatus"=3
GROUP BY 
    "SellerLegalName",
    "SellerTaxCode";