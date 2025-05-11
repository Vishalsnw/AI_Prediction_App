// pages/index.tsx import { useState } from "react"; import { Button } from "@/components/ui/button"; import { Card, CardContent } from "@/components/ui/card"; import { Textarea } from "@/components/ui/textarea";

const categories = [ "Politics", "Weather", "Sports", "Science", "Technology", "Health", "Education", "Stock Market", "Economy", "Business", "Entertainment", "War", "Fashion", "Government" ];

export default function Home() { const [topic, setTopic] = useState("Politics"); const [result, setResult] = useState(""); const [loading, setLoading] = useState(false);

async function generatePrediction() { setLoading(true); setResult("Generating prediction...");

const res = await fetch("/api/predict", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ topic })
});

const data = await res.json();
setResult(data.prediction);
setLoading(false);

}

return ( <div className="max-w-2xl mx-auto p-4"> <h1 className="text-2xl font-bold mb-4 text-center">AI News-Based Prediction App</h1> <select className="w-full border p-2 rounded mb-4" value={topic} onChange={(e) => setTopic(e.target.value)} > {categories.map((cat) => ( <option key={cat} value={cat}>{cat}</option> ))} </select> <Button onClick={generatePrediction} disabled={loading}> {loading ? "Generating..." : "Generate Prediction"} </Button> <Card className="mt-4"> <CardContent> <Textarea className="w-full h-80" value={result} readOnly /> </CardContent> </Card> </div> ); }

                                                                                                                                         
