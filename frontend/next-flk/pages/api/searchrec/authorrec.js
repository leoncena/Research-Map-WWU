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

    const authorrec = await db
      .collection('persons')
      .aggregate([{ $sample: { size: 7 } }])
      .project({ _id: 0, cfFirstNames: 1, cfFamilyNames: 1 })
      .toArray()

    res.json(authorrec)
  } catch (e) {
    console.error(e)
  }
}
