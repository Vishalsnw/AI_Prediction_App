// pages/api/predict.ts import type { NextApiRequest, NextApiResponse } from 'next'; import { OpenAI } from "openai"; import wikipedia from 'wikipedia'; import feedparser from 'feedparser-promised'; import { JSDOM } from 'jsdom'; import { Readability } from '@mozilla/readability';

const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

const getNewsArticles = async (topic: string) => { const rssUrl = https://news.google.com/rss/search?q=${topic}&hl=en-IN&gl=IN; const articles = await feedparser.parse(rssUrl);

let fullText = ""; for (let entry of articles.slice(0, 3)) { try { const res = await fetch(entry.link); const html = await res.text(); const dom = new JSDOM(html, { url: entry.link }); const reader = new Readability(dom.window.document); const article = reader.parse(); fullText += TITLE: ${entry.title}\n${article?.textContent}\n\n; } catch (e) { continue; } } return fullText || "No news found."; };

const getWikipediaSummary = async (topic: string) => { try { const page = await wikipedia.page(topic); const summary = await page.summary(); return summary.extract.slice(0, 800); } catch { return "No Wikipedia summary found."; } };

const getAstrology = () => { const insights = [ "Mars influence indicates bold public moves ahead.", "Saturn may bring delays in resolutions.", "Mercury retrograde could stir up communication gaps.", "Lunar phase signals public emotional reaction.", "Jupiter brings opportunity and financial focus." ]; return insights[Math.floor(Math.random() * insights.length)]; };

const generatePrediction = async (topic: string, news: string, wiki: string, astrology: string) => { const prompt = Topic: ${topic}\n\n[News]\n${news}\n\n[Wikipedia]\n${wiki}\n\n[Astrology]\n${astrology}\n\nGenerate a 7–21 day forecast with concrete developments, decisions, and likely outcomes. No vague advice.;

const chat = await openai.chat.completions.create({ model: "gpt-3.5-turbo", messages: [ { role: "system", content: "You are a reliable future analyst." }, { role: "user", content: prompt } ], temperature: 0.7, max_tokens: 500 });

return chat.choices[0].message.content; };

export default async function handler(req: NextApiRequest, res: NextApiResponse) { const { topic } = req.body; if (!topic) return res.status(400).json({ error: 'Missing topic' });

const news = await getNewsArticles(topic); const wiki = await getWikipediaSummary(topic); const astrology = getAstrology(); const prediction = await generatePrediction(topic, news, wiki, astrology);

res.status(200).json({ prediction }); }

  
