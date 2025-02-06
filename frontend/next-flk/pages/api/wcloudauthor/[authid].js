import clientPromise from '../../../lib/mongodb'

export default async (req, res) => {
  const { authid } = req.query

  try {
    const client = await clientPromise
    const db = client.db('FLK_Web')

    const filter = { author_id: authid }

    const wordcloud = await db
      .collection('publication_wordcloud_data_author')
      .find(filter)
      .toArray()

    res.json(wordcloud)
  } catch (e) {
    console.error(e)
  }
}
