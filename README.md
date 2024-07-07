# Endpoints

## API

- search/all/:
- optimize/:
- save-budget/:
- save-media/:
- remove-media/:
- clear-all/:
- save-bundle/:
- return-user-data/:
- return-media-info/:
- newly-released/:
- staff-picks/:
- search/services/:
- get-upcoming/:
- in-user-watchlist/:

## AUTHENTICATION

- login
- register
- logout
- password-change

## HEROKU

- admin/: for admin
- api/ then any api endpoint
- auth/ then any authentication endpoint
- settings/ then any settings endpoint
- newsletter/ then any newsletter endpoint
- recommendations/ then any recommendations endpoint
- webhooks/ then any webhooks endpoint

## NEWSLETTER

- return-all-posts/:
- return-post/:
- return-page-posts/:

## RECOMMENDATIONS

- generate-data/:
- save-rating/:
- get-recommendations/:
- save-email/:

## SETTINGS

- get-user-settings/:
- update-user-settings/:
- delete-user-account/:
- subscribe/basic/:
- subscribe/premium/:
- subscribe/cancel/:
- user-subscriptions/create/:
- user-subscriptions/renew/:
- user-subscriptions/cancel/:
- user-subscriptions/view/:
- user-subscriptions/generateBundle/:
- user-subscriptions/upcoming/:
- user-subscriptions/recommendations/:
- avail-subscriptions/search/:
- tosCompliance/:
- tosCompliance/update/:
- contact/:
- is-authenticated/:

## WEBHOOKS

- stripe/:
- user-payments/:

### Actions:
- heroku logs --app=streamline-backend --tail: prints command log output

**** PROBLEMS ****
- If watchlist is too large, VCB breaks and dashboard takes forever to load
- If possible, it would be good to cache everything on the site, so navigating away from VCB or dash for example doesn't need a reload every time
- Newsletter / homepage link
- pagination on payment table
- Need to somehow delay some of the stripe calls to the webhook
- Add email notifications to basically everything once we have a domain for an email server
- If a payment is "Active" make it green, not red
- Will turn automation at some point but that should be mostly setup
- Need to check swap, renew, cancel buttons
- domain hosting etc  


