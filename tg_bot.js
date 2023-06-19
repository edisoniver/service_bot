const express = require('express');
const bodyParser = require('body-parser');
const TelegramBot = require('node-telegram-bot-api');
const { MongoClient, ObjectId } = require('mongodb');
const jwt = require('jsonwebtoken');
const secret = 'your_secret_key'; // Replace with your own secret key
const token = '6297179747:AAGoroCZy8Mr8zTR11SP7EVQk6AKcqHtz-k';

const app = express();
app.use(bodyParser.urlencoded({ extended: false }));
app.use(bodyParser.json());

const bot = new TelegramBot(token, {polling: true});
const uri = "mongodb+srv://PeopleService:PlutoniumSpeck12@telegrambot.wx5fzvy.mongodb.net/";
let client = new MongoClient(uri);
let collection;

async function main() {
    try {
        await client.connect();
        console.log('Connected to MongoDB');
        let db = client.db('PeoplesService');
        collection = db.collection('Jobs');

        startBot();
        app.listen(3000, () => console.log('Server is running on port 3000'));

    } catch (e) {
        console.error(e);
    }
}

function startBot() {
    bot.onText(/\/start/, (msg) => {
        const chatId = msg.chat.id;
        const opts = {
            reply_markup: {
                inline_keyboard: [
                    [{ text: 'Menu 📚', callback_data: 'option_1' }],
                    [{ text: 'Post A Job 🔊', callback_data: 'option_3' },
                    { text: 'Account 🫂', callback_data: 'option_2' }]
                ]
            }
        };
        bot.sendMessage(chatId, "Global Service Bot", opts);
    });

    bot.on('callback_query', async (callbackQuery) => {
        const message = callbackQuery.message;
        const data = callbackQuery.data;
    
        if (data.startsWith('job_')) {
            let jobId = data.slice(4);
            await handleJobSelection(message, jobId);
        } else if (data === 'option_1') {
            await handleOption1(message);
        } else if (data === 'option_2') {
            await handleOption2(message);
        } else if (data === 'option_3') {
            await handleOption3(message);
        } else if (data === 'back_to_menu') {
            await handleBackToMenu(message);  // This is the new function you'll create below
        }
    });
}

app.get('/postJob', (req, res) => {
    const token = req.query.token;
    try {
        jwt.verify(token, secret); // Check if token is valid
        res.send(`
            <form action="/postJob" method="post">
                <input type="text" name="job_name" placeholder="Job Name" required />
                <textarea name="job_description" placeholder="Job Description" required></textarea>
                <input type="text" name="location" placeholder="Location" required />
                <input type="number" name="price" placeholder="Price" required />
                <input type="submit" value="Post Job" />
            </form>
        `);
    } catch (err) {
        res.status(401).send('Invalid token');
    }
});

app.post('/postJob', async (req, res) => {
    const { job_name, job_description, location, price } = req.body;
    try {
        await collection.insertOne({ job_name, job_description, location, price });
        res.send('Job posted successfully');
    } catch (e) {
        console.error(e);
        res.status(500).send('Failed to post job');
    }
});

async function handleOption1(message) {
    let jobsCursor = collection.find({});
    let jobs = await jobsCursor.toArray();

    let keyboard = jobs.map(job => [{
        text: job.job_name,
        callback_data: `job_${job._id.toString()}`
    }, {
        text: `$${job.price}`,
        callback_data: `job_${job._id.toString()}`
    }]);

    let opts = {
        reply_markup: {
            inline_keyboard: keyboard
        }
    };

    bot.sendMessage(message.chat.id, `Choose a job`, opts).then(sentMessage => {
        message.message_id = sentMessage.message_id;
    });
    
}

async function handleBackToMenu(message) {
    const chatId = message.chat.id;
    const opts = {
        reply_markup: {
            inline_keyboard: [
                [{ text: 'Menu 📚', callback_data: 'option_1' }],
                [{ text: 'Post A Job 🔊', callback_data: 'option_3' },
                { text: 'Account 🫂', callback_data: 'option_2' }]
            ]
        }
    };
    await bot.editMessageText("Global Service Bot", {chat_id: chatId, message_id: message.message_id, reply_markup: opts.reply_markup});
}


async function handleJobSelection(message, jobId) {
    let objectId = new ObjectId(jobId);
    let job = await collection.findOne({_id: objectId});
    let opts = {
        reply_markup: {
            inline_keyboard: [
                [{ text: 'More Details', url: `http://127.0.0.1:3000/jobDetails?jobId=${jobId}` }],
                [{ text: '⬅️ Back', callback_data: 'back_to_menu' }]
            ]
        }
    };
    if (job) {
        let jobDetails = `
Job Name: ${job.job_name}
Job Description: ${job.job_description}
Location: ${job.location}
Price: $${job.price}
        `;
        await bot.editMessageText(jobDetails, {chat_id: message.chat.id, message_id: message.message_id, reply_markup: opts.reply_markup});
    } else {
        await bot.sendMessage(message.chat.id, `No job was found with ID: ${jobId}`);
    }
}

app.get('/jobDetails', async (req, res) => {
    let jobId = req.query.jobId;
    let objectId = new ObjectId(jobId);
    let job = await collection.findOne({_id: objectId});

    if (job) {
        // Display a detailed page with job details
        // This is just a simple example, you should replace it with your own HTML template
        res.send(`
            <h1>${job.job_name}</h1>
            <p>${job.job_description}</p>
            <p>Location: ${job.location}</p>
            <p>Price: $${job.price}</p>
        `);
    } else {
        res.status(404).send('Job not found');
    }
});


async function handleOption2(message) {
    await bot.sendMessage(message.chat.id, `You selected option 2.`);
}

async function handleOption3(message) {
    let token = jwt.sign({ userId: message.chat.id }, secret, { expiresIn: '1h' });
    let opts = {
        reply_markup: {
            inline_keyboard: [
                [{ text: '🛜Post a Job', url: `http://127.0.0.1:3000/postJob?token=${token}` }],
                [{ text: '⬅️ Back', callback_data: 'back_to_menu' }]
            ]
        }
    };
    await bot.sendMessage(message.chat.id, `Please follow this link to post a job:`, opts);
}


main().catch(console.error);
