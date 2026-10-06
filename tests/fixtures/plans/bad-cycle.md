---
plan_id: bad-cycle
feature: Add billing with Stripe checkout
gitops_app: ika100/shop-gitops
status: draft
repos:
  - id: shop-models
    shape: library-python
    summary: Add Invoice and Subscription models
    arguments: |
      Add Invoice and Subscription pydantic models.
      Export them from the package root.
    depends_on: [shop-web]
    done: false
  - id: shop-api
    shape: service-python
    summary: Add /billing endpoints
    arguments: |
      Add POST /billing/checkout and GET /billing/invoices using the new models.
    depends_on: [shop-nope]
    done: false
  - id: shop-web
    shape: web-nextjs
    summary: Add pricing page and checkout button
    arguments: |
      Add /pricing page that calls the billing API.
    depends_on: [shop-api]
    done: false
gitops_pin:
  - service: shop-api
    overlay: staging
    apply_after: shop-api
    note: pin after API PR merges
  - service: shop-web
    overlay: staging
    apply_after: merge_of_all
    note: pin web last
---

## shop-models — Add Invoice and Subscription models

**Shape:** `library-python` · **Depends on:** [] · **Run:** `/svc:build-feature` with the `arguments` block above.

Models live in `shop_models/billing.py`.

## shop-api — Add /billing endpoints

**Shape:** `service-python` · **Depends on:** [shop-nope]

Endpoints use the models.

## shop-web — Add pricing page and checkout button

**Shape:** `web-nextjs` · **Depends on:** [shop-api]

Pricing page in `app/pricing/page.tsx`.

## gitops-app PR

Pin staging for shop-api then shop-web.
