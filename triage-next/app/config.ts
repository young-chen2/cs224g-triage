// src/config.ts
// Central configuration file

const config = {
    supabase: {
      url: 'https://glywofkvlxetpjaczarj.supabase.co',
      anonKey: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdseXdvZmt2bHhldHBqYWN6YXJqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDA1MjMzODUsImV4cCI6MjA1NjA5OTM4NX0.-eddCtmxOD_QGAcMWdk7H92RgpVn7ioj3w8XdFHllrs',
      serviceKey: 'YOUR_SUPABASE_SERVICE_KEY' // Only needed for server-side operations
    },
    api: {
      baseUrl: 'http://127.0.0.1:8000'
    }
  };
  
  export default config;