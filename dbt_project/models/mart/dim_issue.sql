with source as (
    select distinct
        issue,
        sub_issue
    from {{ ref('stg_cfpb_complaints') }}
    where issue is not null
),

final as (
    select
        hash(coalesce(issue, ''), coalesce(sub_issue, ''))::bigint as issue_key,
        issue,
        sub_issue
    from source
)

select * from final
