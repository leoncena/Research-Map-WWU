import clientPromise from '../../../lib/mongodb'

export default async (req, res) => {
  try {
    // await clientPromise
    // `await clientPromise` will use the default database passed in the MONGODB_URI
    // However you can use another database (e.g. myDatabase) by replacing the `await clientPromise` with the following code:
    //.find({})
    //.project({ cfTitle: 1 })
    const client = await clientPromise
    const db = client.db('FLK_Web')

    const topicrec = await db
      .collection('publications')
      .aggregate([
        { $sample: { size: 100 } },
        { $match: { keywords: { $exists: true, $ne: null } } },
      ])
      .project({ _id: 0, keywords: 1 })
      .limit(7)
      .toArray()

    res.json(topicrec)
  } catch (e) {
    console.error(e)
  }
}
