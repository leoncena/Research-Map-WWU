import clientPromise from '../../../lib/mongodb'

export default async (req, res) => {
  const { authid } = req.query

  try {
    const client = await clientPromise
    const db = client.db('FLK_Web')

    const filter = { id: authid }

    const coauthordata = await db
      .collection('author_networks')
      .find(filter)
      .project({ _id: 0 })
      .toArray()

    res.json(coauthordata[0])
  } catch (e) {
    console.error(e)
  }
}
