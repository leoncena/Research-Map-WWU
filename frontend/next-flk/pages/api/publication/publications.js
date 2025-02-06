import clientPromise from '../../../lib/mongodb'

export default async (req, res) => {
  try {
    const client = await clientPromise
    const db = client.db('FLK_Web')

    const publications = await db
      .collection('publications')
      .find({})
      .limit(5)
      .toArray()

    res.json(publications)
  } catch (e) {
    console.error(e)
  }
}
