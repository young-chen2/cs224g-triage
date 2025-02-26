import { createClient } from '@supabase/supabase-js';

// Initialize the Supabase client
const supabaseUrl = "https://glywofkvlxetpjaczarj.supabase.co";
const supabaseKey = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdseXdvZmt2bHhldHBqYWN6YXJqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDA1MjMzODUsImV4cCI6MjA1NjA5OTM4NX0.-eddCtmxOD_QGAcMWdk7H92RgpVn7ioj3w8XdFHllrs";

const supabase = createClient(supabaseUrl, supabaseKey);

export default supabase;