1. Why we are using the sync worker and not gevent etc? 

Our queues rely on asyncio, running pay-api under gevent causes issues with queues (asyncio wont play nice and states there is an existing loop).

2. What do the payment_date, refund_dates signify in the invoices table?

These are when the invoice has moved to PAID or CANCELLED/CREDITED/REFUNDED. This isn't the exact date the payment has been executed, it's the date that we have received feedback and confirmed the invoice was finalized. These fields were added in there because we only had the created_on, updated_on fields before.. which can easily be overwritten by disbursement.

3. What should I watch out for while doing migrations?

If you are updating a large table (i.e. invoices, invoice_references, etc.) add `op.execute("set statement_timeout=20000;")` to the top of your new migration scripts for upgrade/downgrade. This will prevent the deployment from causing errors in prod when it takes too long to complete (> 20 seconds). If this fails, it's possible to retry.

If this doesn't work, it might be necessary to manually execute the migration.

For example - this kills the database connections, while it executes a manual migration:

```
UPDATE pg_database SET datallowconn = 'false' WHERE datname = 'pay-db';
SELECT pg_terminate_backend(pid)FROM pg_stat_activity WHERE datname = 'pay-db' and application_name <> 'psql'
ALTER TABLE invoices ADD COLUMN disbursement_date TIMESTAMP;
update alembic_version set version_num = '286acad5d366';
UPDATE pg_database SET datallowconn = 'true' WHERE datname = 'pay-db'
```

EX. Migrations should be done in two steps:
Migrations are structure only
Outside of that we migrate / modify the data

This mitgates the risk of a bad migration.

4. Why are we using two different serialization methods (Marshmallow and Cattrs)?

We're slowly converting to Cattrs from Marshmallow, Cattrs is quite a bit faster and more modern. Marshmallow is fairly slow in performance, I've tried installing some helper packages to increase the performance but it's still fairly slow. Cattrs was used for the serialization of invoices (can be up to 60,000 invoices). 

5. Why is the service fee not included when sending a payload for BC Online?

It's not included because it's set on the BC Online side. It's also possible to check this in CPRD. 

6. What is disbursement? 

It's the terminology we use to pay our partners. For example there is EJV disbursement for Ministry partners, we have AP Disbursement (EFT) for Non-Ministry Partners. We debit our internal GL (excluding service fees) and credit an external GL or bank account. 

7. How is the PAY-API spec updated?

Right now it's a manual process.

8. Where is the payment flow documentation? 

There are bits of it everywhere right now, but Louise is building out all of the documentation - will be uploaded to github shortly.

https://github.com/bcgov/sbc-pay/blob/main/docs/docs/architecture/FAS_Intgeration.md
https://github.com/bcgov-registries/documents/blob/main/pay/EJV.md
https://github.com/bcgov-registries/documents/blob/main/pay/PAD.md

Are great starting points.

9. How do I identify stale invoices that aren't being processed (stuck in APPROVED)?

Via query:

pay-db=# select count(*), payment_method_code from invoices where created_on < now() - interval '20' day and invoice_status_code = 'APPROVED' group by payment_method_code;
 count | payment_method_code
-------+---------------------
  1015 | EJV
     1 | INTERNAL
   665 | PAD
(3 rows)

10. Why are there so many routing slip jobs? 

FRCR doesn't allow us to do a PATCH or a PUT on the receipt object. We have to recreate the receipt from scratch for corrections.

11. How do we tell if CAS/CFS are in sync with SBC-PAY? 

Can spot check with invoices and hit the endpoints to compare the values. We're working on something in the future to get a dump of all of CAS/CFS so we can easily compare using that. 

12. Why is there CANCELLED/CREDITED/REFUNDED? 

Because we have no way of executing PAD refunds, we can only credit a CFS account or cancel the transaction before it happens. 

13. How do I get PAD/EJV invoices unstuck out of APPROVED or into their finalized state?

PAD:
We have a few notebooks available - ideally check to see the if the CSV file has processed in the payment reconciliation queue. 

Modify this notebook to look at all invoices, it will query CFS - if the amount_due is > 0, we know it's uncharged or unpaid. 

If amount_due from CFS = 0, it's possible some of the CSV files (take a look at the cas_settlements table) weren't processed. 

https://github.com/bcgov-registries/ops-support/blob/main/support/ops/relationships/datafetch/pad-pending-invoice-query-cas.ipynb

EJV:
We're currently in the process of building a notebook that can assist with this. Basically make sure all of the FEEDBACK files were processed correctly. 
If they weren't or are missing, contact CAS. 

14. How do I execute a partial credit for PAD (we don't do PAD refunds)?

Take a look at this notebook:
https://github.com/bcgov-registries/ops-support/blob/main/support/ops/relationships/datafix/partial-refund-pad.ipynb

15. How can we reconcile payments with CAS/CFS and BCOL? 

It's possible to use CPRD to look at payments in BCOL and match them up to payments in SBC-PAY. 
Example query:

`SELECT * FROM BCONLINE_BILLING_RECORD where key = 'REG01788290';`

For CAS/CFS - we're in the process of building a data warehousing solution so we can query cross database hopefully to line up some results. 

