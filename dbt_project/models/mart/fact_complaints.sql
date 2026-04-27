with stg as (
    select * from {{ ref('stg_cfpb_complaints') }}
),

dim_product   as (select * from {{ ref('dim_product') }}),
dim_company   as (select * from {{ ref('dim_company') }}),
dim_issue     as (select * from {{ ref('dim_issue') }}),
dim_geography as (select * from {{ ref('dim_geography') }}),
dim_date      as (select * from {{ ref('dim_date') }}),

final as (
    select
        hash(stg.complaint_id)::bigint                             as complaint_key,
        stg.complaint_id,
        dp.product_key,
        dc.company_key,
        di.issue_key,
        dg.geography_key,
        dd.date_key,
        stg.submitted_via,
        stg.timely_response_flag,
        stg.consumer_disputed_flag,
        stg.consumer_consent_provided
    from stg
    left join dim_product dp
        on  stg.product = dp.product_name
        and coalesce(stg.sub_product, '') = coalesce(dp.product_category, '')
    left join dim_company dc
        on stg.company = dc.company_name
    left join dim_issue di
        on  stg.issue = di.issue
        and coalesce(stg.sub_issue, '') = coalesce(di.sub_issue, '')
    left join dim_geography dg
        on  stg.state = dg.state
        and coalesce(stg.zip_code, '') = coalesce(dg.zip_code, '')
    left join dim_date dd
        on stg.date_received = dd.full_date
)

select * from final
