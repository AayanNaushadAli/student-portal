import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
database_url = os.getenv("DATABASE_URL")

sql = """
create extension if not exists vector;

drop table if exists document_sections cascade;

create table document_sections (
  id uuid primary key default gen_random_uuid(),
  file_hash text not null,
  content text not null,
  embedding vector(3072) not null
);

create index if not exists idx_doc_sections_file_hash on document_sections (file_hash);

create or replace function match_document_sections (
  query_embedding vector(3072),
  match_threshold float,
  match_count int,
  filter_file_hash text
)
returns table (
  id uuid,
  content text,
  similarity float
)
language plpgsql
as $$
begin
  return query
  select
    document_sections.id,
    document_sections.content,
    1 - (document_sections.embedding <=> query_embedding) as similarity
  from document_sections
  where
    document_sections.file_hash = filter_file_hash
    and (1 - (document_sections.embedding <=> query_embedding)) > match_threshold
  order by document_sections.embedding <=> query_embedding
  limit match_count;
end;
$$;
"""

try:
    conn = psycopg2.connect(database_url)
    with conn.cursor() as cur:
        cur.execute(sql)
        conn.commit()
    print("✅ Database setup complete!")
    conn.close()
except Exception as e:
    print(f"❌ Error during setup: {e}")
