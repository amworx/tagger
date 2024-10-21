import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select } from '@/components/ui/select'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

type AssetCategory = 'office' | 'employee'

export function AssetTagGenerator() {
  const [assetCategory, setAssetCategory] = useState<AssetCategory>('office')
  const [assetNumber, setAssetNumber] = useState('')
  const [assetType, setAssetType] = useState('')
  const [building, setBuilding] = useState('')
  const [roomNumber, setRoomNumber] = useState('')
  const [department, setDepartment] = useState('')
  const [employeeId, setEmployeeId] = useState('')
  const [generatedTag, setGeneratedTag] = useState('')

  const generateTag = () => {
    let tag = ''
    if (assetCategory === 'office') {
      tag = `${assetNumber}-${assetType}-${building}-RN${roomNumber.padStart(3, '0')}`
    } else {
      tag = `${assetNumber}-${assetType}-${department}-ID${employeeId.padStart(3, '0')}`
    }
    setGeneratedTag(tag)
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Asset Tag Generator</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <Label htmlFor="assetCategory">Asset Category</Label>
              <Select
                id="assetCategory"
                value={assetCategory}
                onValueChange={(value: AssetCategory) => setAssetCategory(value)}
              >
                <option value="office">Office Asset</option>
                <option value="employee">Employee-held Asset</option>
              </Select>
            </div>
            <div>
              <Label htmlFor="assetNumber">Asset Number</Label>
              <Input
                id="assetNumber"
                value={assetNumber}
                onChange={(e) => setAssetNumber(e.target.value)}
                placeholder="4-digit number"
              />
            </div>
            <div>
              <Label htmlFor="assetType">Asset Type</Label>
              <Input
                id="assetType"
                value={assetType}
                onChange={(e) => setAssetType(e.target.value)}
                placeholder="3-character code"
              />
            </div>
            {assetCategory === 'office' ? (
              <>
                <div>
                  <Label htmlFor="building">Building</Label>
                  <Input
                    id="building"
                    value={building}
                    onChange={(e) => setBuilding(e.target.value)}
                    placeholder="3-character code"
                  />
                </div>
                <div>
                  <Label htmlFor="roomNumber">Room Number</Label>
                  <Input
                    id="roomNumber"
                    value={roomNumber}
                    onChange={(e) => setRoomNumber(e.target.value)}
                    placeholder="3-digit number"
                  />
                </div>
              </>
            ) : (
              <>
                <div>
                  <Label htmlFor="department">Department</Label>
                  <Input
                    id="department"
                    value={department}
                    onChange={(e) => setDepartment(e.target.value)}
                    placeholder="3-character code"
                  />
                </div>
                <div>
                  <Label htmlFor="employeeId">Employee ID</Label>
                  <Input
                    id="employeeId"
                    value={employeeId}
                    onChange={(e) => setEmployeeId(e.target.value)}
                    placeholder="3-digit number"
                  />
                </div>
              </>
            )}
            <Button onClick={generateTag}>Generate Tag</Button>
          </div>
        </CardContent>
      </Card>
      {generatedTag && (
        <Card>
          <CardHeader>
            <CardTitle>Generated Asset Tag</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{generatedTag}</p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
