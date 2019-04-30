CREATE SEQUENCE public.users_id_seq
  INCREMENT 1
  MINVALUE 1
  MAXVALUE 9223372036854775807
  START 24
  CACHE 1;
ALTER TABLE public.users_id_seq
  OWNER TO test_user;

CREATE TABLE public.users
(
  id integer NOT NULL DEFAULT nextval('users_id_seq'::regclass),
  name character varying,
  surname character varying,
  password character varying,
  email character varying NOT NULL,
  date_created date,
  ext_id character varying,
  CONSTRAINT users_pkey PRIMARY KEY (id),
  CONSTRAINT users_email_key UNIQUE (email)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE public.users
  OWNER TO test_user;

-----

CREATE SEQUENCE public.datasets_id_seq
  INCREMENT 1
  MINVALUE 1
  MAXVALUE 9223372036854775807
  START 47
  CACHE 1;
ALTER TABLE public.datasets_id_seq
  OWNER TO test_user;

CREATE TABLE public.datasets
(
  id integer NOT NULL DEFAULT nextval('datasets_id_seq'::regclass),
  name character varying NOT NULL,
  description character varying,
  user_id integer NOT NULL,
  date_created timestamp without time zone,
  date_updated timestamp without time zone,
  accuracy_degree numeric,
  screen_size numeric,
  screen_res_x integer,
  screen_res_y integer,
  tracker_distance numeric,
  CONSTRAINT datasets_pkey PRIMARY KEY (id),
  CONSTRAINT datasets_user_id_fkey FOREIGN KEY (user_id)
      REFERENCES public.users (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE CASCADE
)
WITH (
  OIDS=FALSE
);

ALTER TABLE public.datasets
  OWNER TO test_user;

-----

CREATE SEQUENCE public.tasks_id_seq
  INCREMENT 1
  MINVALUE 1
  MAXVALUE 9223372036854775807
  START 153
  CACHE 1;
ALTER TABLE public.tasks_id_seq
  OWNER TO test_user;

CREATE TABLE public.tasks
(
  id integer NOT NULL DEFAULT nextval('tasks_id_seq'::regclass),
  name character varying NOT NULL,
  description character varying,
  url character varying,
  dataset_id integer NOT NULL,
  date_created timestamp without time zone,
  date_updated timestamp without time zone,
  scanpath_data_raw jsonb,
  aoi_data jsonb,
  scanpath_data_formatted jsonb,
  CONSTRAINT tasks_pkey PRIMARY KEY (id),
  CONSTRAINT tasks_dataset_id_fkey FOREIGN KEY (dataset_id)
      REFERENCES public.datasets (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE CASCADE
)
WITH (
  OIDS=FALSE
);

ALTER TABLE public.tasks
  OWNER TO test_user;
