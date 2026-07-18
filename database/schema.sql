-- PDF to E-Course Learning Platform — PostgreSQL schema
-- Generated from the SQLAlchemy models (app/models). For reference and manual
-- provisioning; the source of truth for migrations is Alembic (backend/alembic).
-- Enable UUID/JSONB support is native in PostgreSQL 13+.

CREATE TABLE users (
	email VARCHAR(320) NOT NULL, 
	full_name VARCHAR(255), 
	hashed_password VARCHAR(255), 
	avatar_url VARCHAR(1024), 
	auth_provider VARCHAR(50) NOT NULL, 
	supabase_user_id VARCHAR(255), 
	is_active BOOLEAN NOT NULL, 
	is_verified BOOLEAN NOT NULL, 
	is_superuser BOOLEAN NOT NULL, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (supabase_user_id)
);

CREATE UNIQUE INDEX ix_users_email ON users (email);

CREATE INDEX ix_users_id ON users (id);

CREATE TABLE uploads (
	user_id UUID NOT NULL, 
	filename VARCHAR(512) NOT NULL, 
	original_filename VARCHAR(512) NOT NULL, 
	content_type VARCHAR(128) NOT NULL, 
	size_bytes INTEGER NOT NULL, 
	page_count INTEGER NOT NULL, 
	storage_path VARCHAR(1024) NOT NULL, 
	storage_provider VARCHAR(50) NOT NULL, 
	extracted_text TEXT, 
	status VARCHAR(50) NOT NULL, 
	error_message TEXT, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE INDEX ix_uploads_id ON uploads (id);

CREATE INDEX ix_uploads_user_id ON uploads (user_id);

CREATE TABLE courses (
	user_id UUID NOT NULL, 
	upload_id UUID NOT NULL, 
	title VARCHAR(512) NOT NULL, 
	description TEXT, 
	difficulty VARCHAR(50) NOT NULL, 
	estimated_minutes INTEGER NOT NULL, 
	learning_objectives JSONB, 
	prerequisites JSONB, 
	tags JSONB, 
	status VARCHAR(50) NOT NULL, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE, 
	FOREIGN KEY(upload_id) REFERENCES uploads (id) ON DELETE CASCADE
);

CREATE INDEX ix_courses_id ON courses (id);

CREATE INDEX ix_courses_upload_id ON courses (upload_id);

CREATE INDEX ix_courses_user_id ON courses (user_id);

CREATE TABLE embeddings (
	upload_id UUID NOT NULL, 
	chunk_index INTEGER NOT NULL, 
	page_number INTEGER, 
	content TEXT NOT NULL, 
	vector_id VARCHAR(255) NOT NULL, 
	collection_name VARCHAR(255) NOT NULL, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(upload_id) REFERENCES uploads (id) ON DELETE CASCADE
);

CREATE INDEX ix_embeddings_id ON embeddings (id);

CREATE INDEX ix_embeddings_vector_id ON embeddings (vector_id);

CREATE INDEX ix_embeddings_upload_id ON embeddings (upload_id);

CREATE TABLE chat_sessions (
	user_id UUID NOT NULL, 
	course_id UUID NOT NULL, 
	title VARCHAR(512) NOT NULL, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE, 
	FOREIGN KEY(course_id) REFERENCES courses (id) ON DELETE CASCADE
);

CREATE INDEX ix_chat_sessions_id ON chat_sessions (id);

CREATE INDEX ix_chat_sessions_user_id ON chat_sessions (user_id);

CREATE INDEX ix_chat_sessions_course_id ON chat_sessions (course_id);

CREATE TABLE chapters (
	course_id UUID NOT NULL, 
	title VARCHAR(512) NOT NULL, 
	summary TEXT, 
	order_index INTEGER NOT NULL, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(course_id) REFERENCES courses (id) ON DELETE CASCADE
);

CREATE INDEX ix_chapters_course_id ON chapters (course_id);

CREATE INDEX ix_chapters_id ON chapters (id);

CREATE TABLE chat_messages (
	session_id UUID NOT NULL, 
	role VARCHAR(20) NOT NULL, 
	content TEXT NOT NULL, 
	sources JSONB, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(session_id) REFERENCES chat_sessions (id) ON DELETE CASCADE
);

CREATE INDEX ix_chat_messages_session_id ON chat_messages (session_id);

CREATE INDEX ix_chat_messages_id ON chat_messages (id);

CREATE TABLE lessons (
	chapter_id UUID NOT NULL, 
	title VARCHAR(512) NOT NULL, 
	content TEXT, 
	explanation TEXT, 
	examples TEXT, 
	important_notes TEXT, 
	summary TEXT, 
	key_takeaways JSONB, 
	estimated_minutes INTEGER NOT NULL, 
	order_index INTEGER NOT NULL, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(chapter_id) REFERENCES chapters (id) ON DELETE CASCADE
);

CREATE INDEX ix_lessons_chapter_id ON lessons (chapter_id);

CREATE INDEX ix_lessons_id ON lessons (id);

CREATE TABLE quizzes (
	course_id UUID NOT NULL, 
	chapter_id UUID, 
	title VARCHAR(512) NOT NULL, 
	description TEXT, 
	difficulty VARCHAR(50) NOT NULL, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(course_id) REFERENCES courses (id) ON DELETE CASCADE, 
	FOREIGN KEY(chapter_id) REFERENCES chapters (id) ON DELETE CASCADE
);

CREATE INDEX ix_quizzes_id ON quizzes (id);

CREATE INDEX ix_quizzes_course_id ON quizzes (course_id);

CREATE TABLE lesson_progress (
	user_id UUID NOT NULL, 
	lesson_id UUID NOT NULL, 
	completed BOOLEAN NOT NULL, 
	completed_at TIMESTAMP WITH TIME ZONE, 
	time_spent_seconds INTEGER NOT NULL, 
	last_position INTEGER NOT NULL, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_user_lesson UNIQUE (user_id, lesson_id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE, 
	FOREIGN KEY(lesson_id) REFERENCES lessons (id) ON DELETE CASCADE
);

CREATE INDEX ix_lesson_progress_id ON lesson_progress (id);

CREATE INDEX ix_lesson_progress_user_id ON lesson_progress (user_id);

CREATE INDEX ix_lesson_progress_lesson_id ON lesson_progress (lesson_id);

CREATE TABLE quiz_questions (
	quiz_id UUID NOT NULL, 
	question_type VARCHAR(30) NOT NULL, 
	question TEXT NOT NULL, 
	options JSONB, 
	correct_answer TEXT NOT NULL, 
	explanation TEXT, 
	order_index INTEGER NOT NULL, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(quiz_id) REFERENCES quizzes (id) ON DELETE CASCADE
);

CREATE INDEX ix_quiz_questions_quiz_id ON quiz_questions (quiz_id);

CREATE INDEX ix_quiz_questions_id ON quiz_questions (id);

CREATE TABLE quiz_attempts (
	quiz_id UUID NOT NULL, 
	user_id UUID NOT NULL, 
	score FLOAT NOT NULL, 
	total_questions INTEGER NOT NULL, 
	correct_count INTEGER NOT NULL, 
	answers JSONB, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(quiz_id) REFERENCES quizzes (id) ON DELETE CASCADE, 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE INDEX ix_quiz_attempts_user_id ON quiz_attempts (user_id);

CREATE INDEX ix_quiz_attempts_quiz_id ON quiz_attempts (quiz_id);

CREATE INDEX ix_quiz_attempts_id ON quiz_attempts (id);

