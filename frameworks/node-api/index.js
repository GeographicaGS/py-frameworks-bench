
const cluster = require('cluster');
const express = require('express')
const bodyParser = require('body-parser')
const http = require('http');
const app = express()
const port = 5000

if (cluster.isMaster) {
  // Create 2 workers...
  for (var i = 0; i < 2; i += 1) {
      cluster.fork();
  }

} else {

  const Pool = require('pg').Pool
  const pool = new Pool({
    user: 'benchmark',
    host: 'localhost',
    database: 'benchmark',
    password: 'benchmark',
    port: 5432,
  })

  app.use(bodyParser.json())
  app.use(
    bodyParser.urlencoded({
      extended: true,
    })
  )

  app.get('/json', (request, response) => {
    response.json({ message: 'Hello, World!' })
  })

  app.get('/remote', (request, response) => {
    http.get('http://localhost', (resp) => {
      let data = '';

      // A chunk of data has been recieved.
      resp.on('data', (chunk) => {
        data += chunk;
      });

      // The whole response has been received. Print out the result.
      resp.on('end', () => {
        response.json({data: data});
      });

    }).on("error", (err) => {
      console.log("Error: " + err.message);
    });
  })


  app.get('/complete', (request, response) => {
    pool.query('SELECT * FROM message LIMIT 100;', (error, results) => {
      if (error) {
        throw error
      }
      response.status(200).json(results.rows)
    })
  })

  app.listen(port, () => {
    console.log(`Node API running on port ${port}.`)
  })

}




