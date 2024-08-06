SELECT 
    "SellerTaxCode" AS "TaxCode",
    "SellerLegalName",
    Count("Id") as "SendingInvoice"
FROM 
    "MInvoice"."Invoice" 
WHERE 
    "TenantId"='?'
    AND "CreationTime" BETWEEN 'checkpoint' and NOW()
    and "SendTaxStatus"=3
GROUP BY 
    "SellerLegalName",
    "SellerTaxCode";