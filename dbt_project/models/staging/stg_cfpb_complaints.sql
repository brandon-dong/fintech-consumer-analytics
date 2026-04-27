with source as (
    select * from {{ source('raw', 'cfpb_complaints') }}
),

deduped as (
    select *,
        row_number() over (
            partition by complaint_id
            order by loaded_at desc
        ) as row_num
    from source
),

final as (
    select
        complaint_id,
        try_to_date(left(date_received, 10))                 as date_received,
        product,
        sub_product,
        issue,
        sub_issue,
        company,
        state,
        zip_code,
        lower(submitted_via)                                 as submitted_via,
        try_to_date(left(date_sent_to_company, 10))          as date_sent_to_company,
        company_response_to_consumer,
        case
            when upper(timely_response) = 'YES' then true
            when upper(timely_response) = 'NO'  then false
            else null
        end                                                  as timely_response_flag,
        case
            when upper(consumer_disputed) = 'YES' then true
            when upper(consumer_disputed) = 'NO'  then false
            else null
        end                                                  as consumer_disputed_flag,
        consumer_consent_provided,
        loaded_at
    from deduped
    where row_num = 1
)

select * from final
