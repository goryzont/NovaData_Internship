
drop table if exists users;

drop table if exists users_audit;

CREATE table users (
    id SERIAL PRIMARY KEY,
    name TEXT,
    email TEXT,
    role TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE users_audit (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    changed_by TEXT,
    field_changed TEXT,
    old_value TEXT,
    new_value TEXT
);

--Логировать все изменения пользователей (name, email, role),
create or replace function users_audit_log() RETURNS trigger AS $$
    begin
		if old.name is distinct from new.name then
			insert into users_audit(user_id, changed_at, changed_by, field_changed, old_value, new_value)
			values(old.id, now(), current_user, 'name', old.name, new.name);
		end if;

		if old.email is distinct from new.email then
			insert into users_audit(user_id, changed_at, changed_by, field_changed, old_value, new_value)
			values(old.id, now(), current_user, 'email', old.email, new.email);
		end if;

		if old.role is distinct from new.role then
			insert into users_audit(user_id, changed_at, changed_by, field_changed, old_value, new_value)
			values(old.id, now(), current_user, 'role', old.role, new.role);
		end if;

        return new;
    end;
$$ language plpgsql;


create or replace trigger trig_users_audit
before update on users
for each row
execute function users_audit_log();

insert into users(name, email, role)
values('Vova', 'vova@mail.ru', 'data analyst');

update users
set name = 'Vladimir',
	email = 'vladimir@mail.ru',
	role = 'data engineer'
where id = 1;

select * from users_audit ua ;

--id user_id 		changed_at 			changed_by field_changed 	old_value 		new_value
--1	   1		2025-06-22 20:53:51.265	user		name			Vova			Vladimir
--2	   1		2025-06-22 20:53:51.265	user		email			vova@mail.ru	vladimir@mail.ru
--3	   1		2025-06-22 20:53:51.265	user		role			data analyst	data engineer


create extension if not exists pg_cron;

create or replace function users_audit_export() returns text as $$
declare
	path TEXT := '/tmp/users_audit_export_' || to_char(now(), 'YYYY-MM-DD_HH24MI') || '.csv';
	query TEXT;
begin
    query := 'COPY (
        SELECT *
        FROM users_audit
        WHERE changed_at >= CURRENT_DATE
        AND changed_at < CURRENT_DATE + INTERVAL ''1 day''
    ) TO ''' || path || ''' WITH CSV HEADER;';

	execute query;

	return 'Файл успешно сохранён: ' || path;
end;
$$ language plpgsql;


select users_audit_export();

select cron.schedule(
	'job_users_audit',
	'0 3 * * *',
	'select users_audit_export()'
)
