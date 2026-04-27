with complaint_counts as (
    select
        company,
        company_response_to_consumer,
        count(*) as response_count
    from {{ ref('stg_cfpb_complaints') }}
    where company is not null
    group by 1, 2
),

ranked as (
    select
        company,
        company_response_to_consumer as company_response,
        row_number() over (
            partition by company
            order by response_count desc
        ) as rn
    from complaint_counts
),

final as (
    select
        hash(company)::bigint as company_key,
        company               as company_name,
        company_response
    from ranked
    where rn = 1
)

select * from final
