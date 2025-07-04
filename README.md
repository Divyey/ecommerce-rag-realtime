## **Project Overview: E-Commerce RAG System with Real-Time Knowledge Base Updates**


### **Aim**


To develop an e-commerce platform that maintains an up-to-date, searchable knowledge base (vector database) of product information (inventory, price, discounts, etc.) using Retrieval-Augmented Generation (RAG). The system should support both periodic crawling and direct integration with the product database, ensuring real-time accuracy for user queries.


### **Methodology**


- **Direct Integration:**
Connect the backend directly to the product database to detect and process updates in real time.
- **Vectorization:**
Convert updated product data into embeddings and store them in a vector database (Weaviate).
- **RAG Pipeline:**
Use a retrieval-augmented generation approach to answer user queries based on the latest product information.
- **Notifications \& Monitoring:**
Log all updates and optionally notify via Slack/webhooks for transparency and debugging.
- **Frontend:**
Provide a simple Gradio or ReactJS-based UI for user queries and admin operations.




### **Procedure**


#### **1. Database Setup**


- Create a PostgreSQL database with tables for products and update logs.




#### **2. Backend Implementation**


- Build a FastAPI backend with OAuth2/JWT authentication.
- Implement CRUD endpoints for products.
- Log every update in a dedicated table.
- On each update, re-embed product data and update the vector DB.




#### **3. Vector Database Integration**


- Deploy Weaviate locally (Docker/self-hosted).
- Connect backend to Weaviate for vector search and updates.




#### **4. Notification System**


- Optionally, set up a webhook to notify a Slack channel on product updates.




#### **5. Frontend (Gradio/React)**


- Build a simple text-based interface for:
   - Users to ask product-related questions.
   - Admins to add/update product data.




#### **6. Testing \& Monitoring**


- Test end-to-end flow: product update → vector DB update → user query.
- Monitor update logs and notifications for data freshness.




### **Requirements**


- **Frontend:** Gradio (for now), ReactJS+Vite (future)
- **Backend:** Python + FastAPI
- **Auth:** OAuth2/JWT
- **Database:** PostgreSQL
- **Vector Database:** Weaviate
- **AI:** OpenAI embeddings or open-source alternative
- **Tunneling (for webhooks):** Tunnelmole/ngrok
- **Notification:** Slack webhook (optional)
- **Validation:** Pydantic
- **Deployment:** Docker (for local dev), self-hosted or cloud (future)




### **Sample Input/Output**


#### **Product Table Example**


| id | name | description | price | inventory | discount | last_updated |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| 1 | Red T-Shirt | 100% cotton, unisex | 499 | 25 | 10 | 2025-07-04 17:00:00 |


#### **User Query Example**


**Input:**
"What is the current price and stock for the Red T-Shirt?"


**Output (from RAG):**
"The Red T-Shirt is currently priced at ₹499, with 25 units in stock and a 10% discount available."


#### **Product Update Example**


- **Action:** Admin updates inventory from 25 to 20.
- **System:** Logs the change, re-embeds product, updates Weaviate, and (optionally) sends a Slack notification.




### **Workflow Diagrams**


#### **1. User Workflow (Querying Product Info)**


```
[User]
  |
  v
[Frontend (Gradio/React)]
  |
  v
[Backend (FastAPI RAG API)]
  |
  v
[Vector DB (Weaviate) + Product DB]
  |
  v
[Response to User]
```




#### **2. Company Data Updater/Admin Workflow (Updating Products)**


```
[Admin/Updater]
  |
  v
[Frontend (Gradio/React) or API Client]
  |
  v
[Backend (FastAPI)]
  |         \
  v          v
[Update Product DB] -- [Log Update]
  |                       |
  v                       v
[Re-embed & Update Vector DB]
  |
  v
[Optional: Send Notification (Slack/Webhook)]
```




#### **3. Developer/Monitoring Workflow**


```
[Developer]
  |
  v
[Check Update Logs/Product DB]
  |
  v
[Monitor Vector DB Sync]
  |
  v
[Receive Notifications (Slack/Webhook)]
  |
  v
[Debug/Improve System]
```




### **Conclusion**


This project will provide a robust, scalable foundation for an e-commerce platform capable of real-time, accurate product information retrieval using RAG. By combining direct integration, vector search, and a simple user/admin interface, you ensure data freshness, transparency, and a seamless user experience. The modular design allows easy future expansion—such as speech-based queries, external data crawling, or advanced analytics.
